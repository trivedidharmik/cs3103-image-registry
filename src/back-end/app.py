#!/usr/bin/env python3

from flask import Flask, jsonify, abort, request, make_response, session, send_from_directory
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


app = Flask(__name__, static_folder="../front-end", static_url_path='/static')

# Serve static files from the storage folder
@app.route('/storage/<path:filename>')
def serve_image(filename):
    return send_from_directory("../storage", filename)

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
		return app.send_static_file('signin.html')

api.add_resource(SignInStatic,'/signin')

# Static endpoint for register
class RegisterStatic(Resource):
	def get(self):
		return app.send_static_file('register.html')
	
api.add_resource(RegisterStatic, '/register')

class VerifyStatic(Resource):
	def get(self):
		return app.send_static_file('verify.html')

api.add_resource(VerifyStatic, '/verify')

class signOutStatic(Resource):
	def get(self):
		if "user_id" not in session:
			return make_response(jsonify({"message": "Unable to sign out"}), 401)
		return app.send_static_file('signout.html')

api.add_resource(signOutStatic, '/signout')

class landingPage(Resource):
	def get(self):
		if "user_id" not in session:
			return make_response(jsonify({"message": "Unauthorized"}), 401)
		return app.send_static_file("landing_page.html")

api.add_resource(landingPage, '/home')

class userHomePage(Resource):
	def get(self):
		if "user_id" not in session:
			return make_response(jsonify({"message": "Unauthorized"}), 401)
		return app.send_static_file("user_home.html")

api.add_resource(userHomePage, '/user_home')

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
					location_header = f"/users/{user_id}/images"
					return make_response(jsonify({"message": "Login successful"}), 301, {"Location": location_header})
				
				return make_response(jsonify({"message": "Invalid verification token"}), 401)
		
			return make_response(jsonify({"message": "Unable to find token"}), 401)
			
			
		except Exception as e:
			abort(500, description=str(e))

api.add_resource(Verify, "/users/<int:user_id>/verify/<string:token_id>")

class SignIn(Resource):
	def post(self):
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

			if not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
				return make_response(jsonify({"message": "Invalid credentials"}), 401)

			session["user_id"] = user_id

			# location_header = f"/users/{user_id}/images"
			location_header = "/home"
			return make_response(jsonify({"message": "Login successful"}), 301, {"Location": location_header})

		except Exception as e:
			abort(500, description=str(e))
			
api.add_resource(SignIn, "/signin")

class SignOut(Resource):
	def post(self):
		'''Remove session data'''
		session.pop("user_id", None)
		return jsonify({"message": "Logged out successfully"}), 200

api.add_resource(SignOut , '/signout')

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
		
		# Sample command line usage:
		#
		# curl -i -X POST -H "Content-Type: application/json"
		#    -d '{"url": "https://en.wikipedia.org/wiki/Book#/media/File:Gutenberg_Bible,_Lenox_Copy,_New_York_Public_Library,_2009._Pic_01.jpg", "title": "Book", "desc":
		#		  "picture of a book", "visibility": "public"}'
		#         http://cs3103.cs.unb.ca:xxxxx/users/1234/images
		if "user_id" not in session or session["user_id"]!=user_id:
			return make_response(jsonify({"message": "Unauthorized"}), 401)

		# TODO: Determine how to separate file name from file extension when uploading, there wont be a second form entry for just the extension
		file = request.form.get('imageFile')
		# fileName = request.form.get('fileName')
		# fileExtension = request.form.get('fileExtension')
		title = request.form.get('title')
		desc = request.form.get('desc')
		visibility = request.form.get('visibility')

		if not title or not visibility or not file:
			abort(400, description="Missing required fields")
		
		# Save the file to the storage directory
		filename = file.filename
		filename = filename.strip().replace(" ", "_")
		filename = "".join(c for c in filename if c.isalnum() or c in ("_", "."))

		file_extension = filename.split('.')[-1]
		file_path = os.path.join('storage', filename)
		file.save(file_path)
	
		sqlProc = 'insertImage'
		sqlArgs = [user_id, filename, file_extension, title, desc, visibility]
		try:
			row = db_access(sqlProc, sqlArgs)
		except Exception as e:
			abort(500, message = e) # server error
		# Look closely, Grasshopper: we just created a new resource, so we're
		# returning the uri to it, based on the return value from the stored procedure.
		# Yes, now would be a good time check out the procedure.
		uri = f"/images/{row[0]['LAST_INSERT_ID()']}"
		return make_response(jsonify( { "uri" : uri } ), 201) # successful resource creation
	
	
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
		if img["visibility"] == "private":
	
			if "user_id" not in session or session["user_id"]!=img["user_id"]:
				return make_response(jsonify({"message": "Unauthorized"}), 401)

		return make_response(jsonify({"image": row}), 200)

	def post(self, image_id):
		# POST: Update a given image contents
		title = request.form.get('title')
		desc = request.form.get('desc')
		visibility = request.form.get('visibility')

		sqlProc = "updateImageData"
		sqlArgs = [image_id, title, desc, visibility]

		try:
			row = db_access(sqlProc, sqlArgs)
		except Exception as e:
			abort(500, message = e)
		uri = request.base_url+'/'+str(row[0]['LAST_INSERT_ID()'])
		return make_response(jsonify({"uri": uri}), 201)

class Search(Resource):
	# GET: Return all images with matching title/visibility (only shows private images of user who is signed in)
	#
	# Example request: curl http://cs3103.cs.unb.ca:xxxxx/images/search/?title=Book&visibility=private
	def get(self):

		if not request.json:
			abort(400)
		
		# Need to search by either title, visibility or both
		if "title" in request.json:
			title = request.json["title"]
			sqlProc = 'searchImagesByTitle'
			sqlArgs = [title] # might need trailing , after title in args
			try:
				title_rows = db_access(sqlProc, sqlArgs)
			except Exception as e:
				abort(500, message = e) # server error

		if "visibility" in request.json:
			visibility = request.json["visibility"]
			sqlProc = 'filterImagesByVisibility'
			sqlArgs = [visibility]
			try:
				visibility_rows = db_access(sqlProc, sqlArgs)
			except Exception as e:
				abort(500, message = e) # server error
		
		if title_rows == None and visibility_rows == None:
			abort(400)
		
		if visibility_rows == None:
			rows = title_rows
		
		elif title_rows == None:
			rows = visibility_rows
		
		# Searching by title and visibility, so take only the elements that exist in both
		else:
			rows = list(set(title_rows) & set(visibility_rows))
		imgs_visible = []
		for img in rows:
			if img["visibility"] == "private":
				if "user_id" not in session or session["user_id"]==img["user_id"]:
					imgs_visible.append(img)
			else:
				imgs_visible.append(img)
	
		return make_response(jsonify({'images': imgs_visible}), 200) # turn set into json and return it

class MostActive(Resource):
	def get(self):
		# GET: Get the most active user(s) -> Admin only
		sqlProc = "getMostActiveUploaders"
		sqlArgs = []

		try:
			rows = db_access(sqlProc, sqlArgs)
		except Exception as e:
			abort(500, message = e)
		return make_response(jsonify({"users": rows}), 200)
	
class CascadeDelete(Resource):
	def delete(self, user_id):
		# DELETE: Cascade delete a user, including all of their images -> Admin only
		if "user_id" not in session or session["user_id"]!=user_id:
			return make_response(jsonify({"message": "Unauthorized"}), 401)

		sqlProc = "deleteUser"
		sqlArgs = [user_id]

		try:
			success = db_access(sqlProc, sqlArgs)
		except Exception as e:
			abort(500, message = e)
		return make_response(jsonify({"success": success}), 200)

	
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
api.add_resource(CascadeDelete, '/delUser')


#############################################################################
if __name__ == "__main__":
	app.run(host=settings.APP_HOST, port=settings.APP_PORT, debug=settings.APP_DEBUG)
