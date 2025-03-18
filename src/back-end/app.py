#!/usr/bin/env python3

from flask import Flask, jsonify, abort, request, make_response
from flask_restful import Resource, Api
import pymysql.cursors
import json

import cgitb
import cgi
import sys
cgitb.enable()

from db_util import db_access
import settings # Our server and db settings, stored in settings.py

app = Flask(__name__, static_url_path='/static')
api = Api(app)


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
		return app.send_static_file('../front-end/index.html')

api.add_resource(Root,'/')

# Static endpoint for sign in
class SignInStatic(Resource):
	def get(self):
		return app.send_static_file('../front-end/signin.html')

api.add_resource(SignInStatic,'/signin')

# Static endpoint for register
class RegisterStatic(Resource):
	def get(self):
		return app.send_static_file('../front-end/register.html')
	
api.add_resource(RegisterStatic, '/register')

####################################################################################
#
# Specific user endpoints
#
class Images(Resource):
	
	def get(self, user_id):
		# GET: Return all images for a user
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
        #         http://cs3103.cs.unb.ca:xxxxx/users/<int:user_id>/images

		if not request.json:
			abort(400) # bad request
		if not 'url' in request.json or not 'title' in request.json or not 'desc' in request.json or not 'visibility' in request.json:
			abort(400)

		# The request object holds the ... wait for it ... client request!
		# Pull the results out of the json request
		url = request.json['url']
		title = request.json['title']
		desc = request.json['desc']
		visibility = request.json['visibility']

		sqlProc = 'createSchool'
		sqlArgs = [user_id, url, title, desc, visibility]
		try:
			row = db_access(sqlProc, sqlArgs)
		except Exception as e:
			abort(500, message = e) # server error
		# Look closely, Grasshopper: we just created a new resource, so we're
		# returning the uri to it, based on the return value from the stored procedure.
		# Yes, now would be a good time check out the procedure.
		uri = request.base_url+'/'+str(row[0]['LAST_INSERT_ID()'])
		return make_response(jsonify( { "uri" : uri } ), 201) # successful resource creation

class School(Resource):
    # GET: Return identified school resource
	#
	# Example request: curl http://cs3103.cs.unb.ca:xxxxx/schools/2
	def get(self, schoolId):
		sqlProc = 'getSchool'
		sqlArgs = [schoolId,]
		try:
			rows = db_access(sqlProc, sqlArgs)
		except Exception as e:
			abort(500, message = e) # server error
		return make_response(jsonify({'schools': rows}), 200) # turn set into json and return it

    # DELETE: Delete identified school resource
    #
    # Example request: curl -X DELETE http://cs3103.cs.unb.ca:xxxxx/schools/2
	def delete(self, schoolId):
		print("SchoolId to delete: "+str(schoolId))
		# 1. You need to create the stored procedure in MySQLdb (deleteSchool)
		# 2. You need to write the code here to call the stored procedure
		# 3. What should/could the response code be? How to return it?
		# 4. Anytime you change a database, you need to commit that change.
		#       See the POST example for more
		sqlProc = 'deleteSchool'
		sqlArgs = [schoolId,]
		try:
			rows = db_access(sqlProc, sqlArgs)
		except Exception as e:
			abort(500, message = e)
		return make_response('', 200)
####################################################################################
#
# Identify/create endpoints and endpoint objects
#
api = Api(app)
api.add_resource(Images, '/users/<int:user_id>/images')
#api.add_resource(School, '/schools/<int:schoolId>')


#############################################################################
# xxxxx= last 5 digits of your studentid. If xxxxx > 65535, subtract 30000
if __name__ == "__main__":
#    app.run(host="cs3103.cs.unb.ca", port=xxxx, debug=True)
	app.run(host=settings.APP_HOST, port=settings.APP_PORT, debug=settings.APP_DEBUG)
