import os
import logging
import simplejson as json
from flasgger import Swagger
from flasgger import swag_from
from flask import Flask, request
from app_server.http_functions import *
from app_server.authentication import authentication_bp
from app_server.videos import videos_bp
from app_server.users import users_bp
from app_server.time import time_bp
from app_server.push_notifications import notifications_bp

from app_server.users import *

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	# Parametro adicional que no estamos usando por ahora en app.config.from_mapping
	#DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'
	app.config.from_mapping(SECRET_KEY='dev')
	Swagger(app)

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

	# Set up del log
	# Basicamente lo que se esta haciendo es usar el handler de gunicorn para
	# que todos los logs salgan por ese canal.
	gunicorn_logger = logging.getLogger('gunicorn.error')
	app.logger.handlers = gunicorn_logger.handlers
	app.logger.setLevel(gunicorn_logger.level)

	app.logger.debug('Log configuration finished')
	app.logger.info('App server running...')

	# Registro de blueprints que encapsulan comportamiento:
	with app.app_context():
		app.register_blueprint(authentication_bp)
		app.register_blueprint(videos_bp)
		app.register_blueprint(users_bp)
		app.register_blueprint(notifications_bp)
		app.register_blueprint(time_bp)

	@app.route('/api/ping/', methods=['GET'])
	@swag_from('docs/ping.yml')
	def _respond():
		api_ping = '/api/ping/'
		response_auth_server = get_auth_server_request(os.environ.get('AUTH_SERVER_URL') + api_ping)
		response_media_server = get_media_server_ping(os.environ.get('MEDIA_SERVER_URL') + api_ping)
		status = {}
		status['App Server'] = 'OK'

		if response_auth_server.status_code == 200:
			app.logger.debug('Response from auth server ping is 200')
			data = response_auth_server.json()
			status['Auth Server'] = data['Health']
		else:
			app.logger.debug('Response from auth server ping is NOT 200')
			status['Auth Server'] = 'DOWN'

		if response_media_server.status_code == 200:
			app.logger.debug('Response from media server ping is 200')
			data = response_media_server.json()
			status['Media Server'] = data['Health']
		else:
			app.logger.debug('Response from media server ping is NOT 200')
			status['Media Server'] = 'DOWN'

		return json.dumps(status)

	@app.route('/api/about/', methods=['GET'])
	@swag_from('docs/about.yml')
	def _about():
		status = {}
		status['Description'] = 'This is Application Server for chotuve-10. Still in construction'
		return json.dumps(status)


	@app.route('/')
	def _index():
		return '<h1>Welcome to application server !</h1>'

### Métodos que aún no implementaremos ###

	@app.route('/api/home/', methods=['GET'])
	@swag_from('docs/home.yml')
	def _home_page():
		return {}

	return app
