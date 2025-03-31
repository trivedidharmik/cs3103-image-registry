#!/usr/bin/env python3

from flask import Flask, jsonify, abort, request, make_response, session, send_from_directory, render_template, redirect, url_for
from flask_restful import Resource, Api
from flask_session import Session
import pymysql.cursors
import json

import cgitb
import cgi
import sys
import bcrypt
cgitb.enable()

from db_util import db_access
from email_util import send_verify_email
import settings # Our server and db settings, stored in settings.py
import os
import uuid

app = Flask(__name__, static_folder="../front-end", static_url_path='/static', template_folder="../front-end")

@app.route('/storage/<path:filename>')
def serve_image(filename):
	# Get image metadata from the database
	sqlProc = 'getImageByFileName'
	sqlArgs = [filename]
	try:
		image_data = db_access(sqlProc, sqlArgs)
	except Exception as e:
		abort(404, description="Image not found")

	if not image_data:
		abort(404, description="Image not found")

	image = image_data[0]
	visibility = image["isVisible"]
	owner_id = image["userId"]

	# Public image: allow access to anyone
	if visibility == "public":
		storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'storage'))
		return send_from_directory(storage_dir, filename)

	# Private image: require logged-in user and ownership
	if "user_id" not in session or session["user_id"] != owner_id:
		abort(403, description="Unauthorized access to private image")

	storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'storage'))
	return send_from_directory(storage_dir, filename)

api = Api(app)

app.secret_key = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'imageRegistry'
app.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST
Session(app)

####################################################################################
#
# Error handlers
#
@app.errorhandler(400) # decorators to add to 400 response
def not_found(error):
	return make_response(jsonify( { "status": "Bad request" } ), 400)

@app.errorhandler(404) # decorators to add to 404 response
def not_found(error):
	return make_response(jsonify( { "status": "Resource not found" } ), 404)

####################################################################################
#
# Static Endpoints for humans
#

# Root home page with sign in button
class Root(Resource):
	def get(self):
		return app.send_static_file('index.html')

api.add_resource(Root,'/')

# Static endpoint for sign in
class SignInStatic(Resource):
	def get(self):
		if "user_id" in session:
			return redirect(url_for('landing_page'))
		return app.send_static_file('signin.html')

api.add_resource(SignInStatic,'/signin')

# Static endpoint for register
class RegisterStatic(Resource):
	def get(self):
		return app.send_static_file('register.html')
	
api.add_resource(RegisterStatic, '/register')

class VerifyStatic(Resource):
	def get(self):
		if "user_id" in session:
			return redirect(url_for('landing_page'))
		return app.send_static_file('verify.html')

api.add_resource(VerifyStatic, '/verify')

# class signOutStatic(Resource):
# 	def get(self):
# 		if "user_id" not in session:
# 			return make_response(jsonify({"message": "Unable to sign out"}), 401)
# 		return app.send_static_file('signout.html')

# api.add_resource(signOutStatic, '/signout')

@app.route('/home')
def landing_page():
	if "user_id" not in session:
		return redirect(url_for('signin'))
	
	keyword = request.args.get('q')  # Get search term
	if keyword:
		sqlProc = 'searchImages'
		sqlArgs = [keyword]
	else:
		sqlProc = 'filterImagesByVisibility'
		sqlArgs = ['public']
	
	try:
		images = db_access(sqlProc, sqlArgs)
	except Exception as e:
		abort(500, description=str(e))
	
	return render_template(
		"landing_page.html",
		images=images,
		is_admin=session.get("is_admin", False))

@app.route("/user_home")
def user_home():
	if "user_id" not in session:
		return redirect(url_for('signin'))
	
	# Get user details
	user_data = db_access('getUserById', [session["user_id"]])
	if not user_data:
		abort(404, description="User not found")
	
	user = user_data[0]
	return render_template(
		"user_home.html",
		is_admin=session.get("is_admin", False),
		user_id=session["user_id"],
		username=user['username'],
		email=user['email']
	)


####################################################################################
#
# Specific user endpoints
#

class Register(Resource):
	def post(self):

		username = request.form.get("username")
		email = request.form.get("email")
		password = request.form.get("password")
		if not username:
			abort(400, description="Missing username")
		if not email:
			abort(400, description="Missing email")
		if not password:
			abort(400, description="Missing password")
		
		hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
		sqlProc = 'registerUser'
		sqlArgs = [username, email, hashed_pw]

		try:
			verify_data = db_access(sqlProc , sqlArgs)
		except Exception as e:
			abort(500, description=str(e))

		# registerUser/generateVerificationToken procedures return created user_id and verification token to use in the url sent to email
		user_id = verify_data[0]["userId"]
		token = verify_data[0]["token"]
		# Ensure token is a string (decode if it's bytes)
		if isinstance(token, bytes):
			try:
				token = token.decode('utf-8') 
			except UnicodeDecodeError:
				token = token.hex()
		verify_url = f"http://{settings.APP_HOST}:{settings.APP_PORT}/users/{user_id}/verify/{token}"

		try:
			send_verify_email(email, verify_url)
		except Exception as e:
			abort(500, description=str(e))
		
		location_header = "/verify"
		return make_response(jsonify({"message": "Registration successful. Please verify your email."}), 301, {"Location": location_header})

api.add_resource(Register, "/register")

class Verify(Resource):
	def get(self, user_id, token_id):
		sqlProc = "verifyEmail"
		sqlArgs = [user_id, token_id]

		try:
			result = db_access(sqlProc, sqlArgs)
			if result:
				if result[0]["success"] == 1:
					session["user_id"] = user_id
					location_header = f"/home"
					return make_response(jsonify({"message": "Login successful"}), 301, {"Location": location_header})
				
				return make_response(jsonify({"message": "Invalid verification token"}), 401)
		
			return make_response(jsonify({"message": "Unable to find token"}), 401)
			
			
		except Exception as e:
			abort(500, description=str(e))

api.add_resource(Verify, "/users/<int:user_id>/verify/<string:token_id>")

class SignIn(Resource):
	def post(self):
		if request.is_json:
			data = request.get_json()
			email = data.get("email")
			password = data.get("password")
		else:
			email = request.form.get("email")
			password = request.form.get("password")

		if not email or not password:
			abort(400, description="Missing email or password")


		sqlProc = 'getUserByEmail'
		sqlArgs = [email]
		try:      
			user_data = db_access(sqlProc , sqlArgs)
			if not user_data:
				return make_response(jsonify({"message": "Invalid credentials"}), 401)

			stored_hash = user_data[0]["passwordHash"]
			user_id = user_data[0]["userId"]
			# Check if email is verified (exists in ValidatedEmails)
			check_verified_proc = 'checkEmailVerified'
			check_verified_args = [user_id]
			verification_result = db_access(check_verified_proc, check_verified_args)
			
			if not verification_result:
				return make_response(jsonify({"message": "Email not verified"}), 401)

			if not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
				return make_response(jsonify({"message": "Invalid credentials"}), 401)

			session["user_id"] = user_id
			session["is_admin"] = user_data[0]["isAdmin"] == 1

			# location_header = f"/users/{user_id}/images"
			location_header = "/home"
			return make_response(jsonify({"message": "Login successful"}), 301, {"Location": location_header})

		except Exception as e:
			abort(500, description=str(e))
			
api.add_resource(SignIn, "/signin")

class SignOut(Resource):
	# Handle GET requests (direct URL access)
	def get(self):
		if "user_id" in session:
			session.pop("user_id", None)
			session.pop("is_admin", None)
		else:
			return redirect(url_for('signin'))
		return app.send_static_file('signout.html')

	# Handle POST requests (sign-out button click)
	def post(self):
		session.pop("user_id", None)
		session.pop("is_admin", None)
		return redirect(url_for('SignOut'))

api.add_resource(SignOut, '/signout')

class UserUpdate(Resource):
	def post(self, user_id):
		if "user_id" not in session or session["user_id"] != user_id:
			return make_response(jsonify({"message": "Unauthorized"}), 401)
		
		data = request.get_json()
		errors = {}
		
		try:
			# Verify current password
			user_data = db_access('getUserById', [user_id])
			if not bcrypt.checkpw(data['currentPassword'].encode('utf-8'), 
								user_data[0]['passwordHash'].encode('utf-8')):
				errors['currentPassword'] = "Incorrect password"
				return jsonify(success=False, errors=errors)
			
			update_args = [user_id]
			proc = 'updateUser'
			
			# Check username availability
			if data['newUsername'] != user_data[0]['username']:
				existing = db_access('getUserByUsername', [data['newUsername']])
				if existing:
					errors['newUsername'] = "Username not available"
					return jsonify(success=False, errors=errors)
				update_args.append(data['newUsername'])
			else:
				update_args.append(None)
			
			# Handle email change
			if data['newEmail'] != user_data[0]['email']:
				update_args.append(data['newEmail'])
				# Generate new verification token
				token_proc = db_access('generateVerificationToken', [user_id])
				token = token_proc[0]['token']
				verify_url = f"http://{settings.APP_HOST}:{settings.APP_PORT}/users/{user_id}/verify/{token}"
				send_verify_email(data['newEmail'], verify_url)
			else:
				update_args.append(None)
			
			# Handle password change
			if data['newPassword']:
				hashed_pw = bcrypt.hashpw(data['newPassword'].encode('utf-8'), 
										bcrypt.gensalt()).decode('utf-8')
				update_args.append(hashed_pw)
			else:
				update_args.append(None)
			
			db_access(proc, update_args)
			return jsonify(
				success=True,
				requiresVerification='newEmail' in data and data['newEmail'] != user_data[0]['email']
			)
			
		except Exception as e:
			return jsonify(success=False, errors={'general': str(e)})

class UserImages(Resource):
	
	def get(self, user_id):
		# GET: Return all images for a user
		if "user_id" not in session or session["user_id"]!=user_id:
			return make_response(jsonify({"message": "Unauthorized"}), 401)

		sqlProc = 'getUserImages'
		sqlArgs = [user_id]
		try:
			rows = db_access(sqlProc, sqlArgs)
		except Exception as e:
			abort(500, message = e) # server error
		return make_response(jsonify({'images': rows}), 200) # turn set into json and return it

	def post(self, user_id):
		# POST: Add a new image
		if "user_id" not in session or session["user_id"] != user_id:
			return make_response(jsonify({"message": "Unauthorized"}), 401)

		file = request.files.get('imageFile')
		title = request.form.get('title')
		desc = request.form.get('desc')
		isVisible = request.form.get('isVisible')

		if not title or not isVisible or not file:
			abort(400, description="Missing required fields")

		# Generate unique filename using UUID
		original_filename = file.filename
		
		# Get file extension (safely handle files without extensions)
		file_extension = original_filename.split('.')[-1] if '.' in original_filename else ''
		
		# Create UUID-based filename
		unique_id = uuid.uuid4().hex  # Generates 32-char string like 'd7a5e8c4b3...'
		new_filename = f"{unique_id}.{file_extension}" if file_extension else unique_id

		# Save to storage
		storage_dir = os.path.abspath(
			os.path.join(os.path.dirname(__file__), '..', '..', 'storage')
		)
		file_path = os.path.join(storage_dir, new_filename)

		# Ensure storage directory exists
		if not os.path.exists(storage_dir):
			os.makedirs(storage_dir, exist_ok=True)
		
		try:
			file.save(file_path)
		except Exception as e:
			abort(500, description=f"Failed to save file: {str(e)}")

		# Store in database
		sqlProc = 'insertImage'
		sqlArgs = [user_id, new_filename, file_extension, title, desc, isVisible]
		
		try:
			row = db_access(sqlProc, sqlArgs)
		except Exception as e:
			# Clean up the saved file if DB insert fails
			if os.path.exists(file_path):
				os.remove(file_path)
			abort(500, message=str(e))

		uri = f"/images/{row[0]['newImageId']}"
		return make_response(jsonify({"uri": uri}), 201)
	
	def delete(self, user_id):
		# DELETE: Delete identified image
		#
		# Example request: curl -X DELETE http://cs3103.cs.unb.ca:xxxxx/users/1234/images '{"image_id": 3}'
		if "user_id" not in session or session["user_id"]!=user_id:
			return make_response(jsonify({"message": "Unauthorized"}), 401)

		if not request.json or "image_id" not in request.json:
			abort(400)
		
		image_id = request.json["image_id"]
		print("Image id to delete: " + str(image_id))
		sqlProc = 'deleteImage'
		sqlArgs = [image_id, user_id]
		try:
			rows = db_access(sqlProc, sqlArgs)
		except Exception as e:
			abort(500, message = e)
		return make_response('', 200)

class ImageCount(Resource):
	def get(self, user_id):
		# GET: Returns the amount of images for the specified user id
		if "user_id" not in session or session["user_id"]!=user_id:
			return make_response(jsonify({"message": "Unauthorized"}), 401)

		sqlProc = "getUserImageCount"
		sqlArgs = [user_id]
		try:
			count = db_access(sqlProc, sqlArgs)
		except Exception as e:
			abort(500, message = e)
		
		return make_response(jsonify({"count": count}), 200)

class Image(Resource):
	def get(self, image_id):
		# GET: Get a specific image by image id (only show private image if its user matches the user who is signed in)
		# TODO: Make stored procedure for this
		
		sqlProc = "getImage"
		sqlArgs = [image_id]
		try:
			row = db_access(sqlProc, sqlArgs)
		except Exception as e:
			abort(500, message = e)
		
		img = row[0]
		if img["isVisible"] == "private":
	
			if "user_id" not in session or session["user_id"]!=img["userId"]:
				return make_response(jsonify({"message": "Unauthorized"}), 401)

		return make_response(jsonify({"image": row}), 200)

	def post(self, image_id):
		# POST: Update a given image contents
		if request.is_json:
			data = request.get_json()
			title = data.get("title")
			desc = data.get("desc")
			isVisible = data.get("isVisibile")
		else:
			title = request.form.get('title')
			desc = request.form.get('desc')
			isVisible = request.form.get('isVisible')
		# Verify ownership
		sqlProc = "getImageOwner"
		sqlArgs = [image_id]
		try:
			owner_data = db_access(sqlProc, sqlArgs)
			if not owner_data or owner_data[0]["userId"] != session["user_id"]:
				abort(403, description="Unauthorized to edit this image")
		except Exception as e:
			abort(500, description=str(e))

		sqlProc = "updateImageData"
		sqlArgs = [image_id, title, desc, isVisible]
		try:
			db_access(sqlProc, sqlArgs)
			return make_response(jsonify({"message": "Image updated successfully"}), 200)
		except Exception as e:
			abort(500, description=str(e))

class Search(Resource):
	def get(self):
		# Get search query from URL parameters
		keyword = request.args.get('q')
		if not keyword:
			abort(400, description="Missing search query")

		sqlProc = 'searchImagesByTitle'
		sqlArgs = [keyword]
		try:
			rows = db_access(sqlProc, sqlArgs)
		except Exception as e:
			abort(500, description=str(e))
		
		# Return results directly (stored procedure ensures visibility is public)
		return make_response(jsonify({'images': rows}), 200)	

class MostActive(Resource):
    def get(self):
        try:
            rows = db_access("getMostActiveUploaders", [])  
        except Exception as e:
            abort(500, message=str(e))

        top3_users = []
        for row in rows:
            userId = row["userId"]
            user_data = db_access("getUserById", [userId])  # Must write a procedure that returns {username, userId, etc.}
            username = user_data[0]["username"] if user_data else "Unknown"
            imageCount = row["imageCount"]
            top3_users.append({
                "userId": userId,
                "username": username,
                "imageCount": imageCount
            })

        return jsonify({"users": top3_users})

	
class CascadeDelete(Resource):
	def delete(self, user_id):
		# DELETE: Cascade delete a user (admin only)
		if "user_id" not in session or not session.get("is_admin", False):
			return make_response(jsonify({"message": "Unauthorized"}), 401)

		sqlProc = "deleteUser"
		sqlArgs = [user_id]

		try:
			success = db_access(sqlProc, sqlArgs)
			return make_response(jsonify({"success": success}), 200)
		except Exception as e:
			abort(500, description=str(e))

@app.route('/admin/manageusers')
def manage_users():
	if "user_id" not in session or not session.get("is_admin", False):
		abort(403, description="Admin access required")
	
	try:
		users = db_access('getAllUsers', [])
	except Exception as e:
		abort(500, description=str(e))
	
	return render_template("manage_users.html", users=users)
####################################################################################
#
# Identify/create endpoints and endpoint objects
#
api = Api(app)
api.add_resource(UserImages, '/users/<int:user_id>/images')
api.add_resource(ImageCount, '/users/<int:user_id>/image-count')
api.add_resource(Image, '/images/<int:image_id>')
api.add_resource(Search, '/images/search')
api.add_resource(MostActive, '/analytics/most-active')
api.add_resource(CascadeDelete, '/admin/users/<int:user_id>')
api.add_resource(UserUpdate, '/users/<int:user_id>/update')


#############################################################################
if __name__ == "__main__":
	app.run(host=settings.APP_HOST, port=settings.APP_PORT, debug=settings.APP_DEBUG)
