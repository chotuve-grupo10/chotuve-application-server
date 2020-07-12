import datetime
import logging
import pytz
from flasgger import swag_from
from flask import Blueprint

time_bp = Blueprint('time', __name__)
logger = logging.getLogger('gunicorn.error')

@time_bp.route('/api/time', methods=["GET"])
@swag_from('docs/get_server_time.yml')
def _get_server_time():
	my_tz = pytz.timezone('America/Argentina/Buenos_Aires')
	date_time = datetime.datetime.now(tz=my_tz)
	formatted_time = date_time.strftime("%Y-%m-%d") + " " + date_time.strftime("%H:%M:%S.%f")
	logger.debug("Current server formatted time %s (timezone is %s)", formatted_time, my_tz)

	return {'Server_time': formatted_time}, 200
