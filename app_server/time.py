import datetime
import logging
import pytz
from flasgger import swag_from
from flask import Blueprint

time_bp = Blueprint('time', __name__)
logger = logging.getLogger('gunicorn.error')

MY_TZ = 'America/Argentina/Buenos_Aires'

@time_bp.route('/api/time', methods=["GET"])
@swag_from('docs/get_server_time.yml')
def _get_server_time():
	formatted_time = get_local_timestamp()
	logger.debug("Current server formatted time %s (timezone is %s)", formatted_time, MY_TZ)

	return {'Server_time': formatted_time}, 200

def get_local_timestamp():
	my_tz = pytz.timezone(MY_TZ)
	date_time = datetime.datetime.now(tz=my_tz)
	return date_time.strftime("%Y-%m-%d") + " " + date_time.strftime("%H:%M:%S.%f")
