from flask import Flask, request
import os
# La documentación de Flask dice que SIMPLEJSON funciona más rápido y que Flask está bien integrado con este
import simplejson as json 

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
	    SECRET_KEY='dev' #,
	    #DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
	)

	if test_config is None:
	    # load the instance config, if it exists, when not testing
	    app.config.from_pyfile('config.py', silent=True)
	else:
	    # load the test config if passed in
	    app.config.from_mapping(test_config)

	# ensure the instance folder exists
	try:
	    os.makedirs(app.instance_path)
	except OSError:
	    pass

	@app.route('/ping/', methods=['GET'])
	def respond():

	    response = {}
	    response["Status"] = "Running"
	    return json.dumps(response)

	@app.route('/hello/')
	def hello():
	    return 'Hello, World!'

	# @app.route('/user/<username>')
	# def show_user_profile(username):
	#     # show the user profile for that user
	#     return 'User name is %s' % escape(username)

	# @app.route('/post/<int:post_id>')
	# def show_post(post_id):
	#     # show the post with the given id, the id is an integer
	#     return 'Post %d' % post_id

	@app.route('/about/')
	def about():
	    return 'This is Application Server for chotuve-10. Still in construction'


	@app.route('/')
	def index():
	    return "<h1>Welcome to application server !</h1>"

	return app
