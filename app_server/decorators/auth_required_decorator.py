from functools import wraps
from flask import g, request, redirect, url_for, current_app
from app_server.token_functions import validate_token

TOKEN_HEADER = 'Authorization'

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get(TOKEN_HEADER)
        if token is None:
            return {'Error' : 'Missing token ({0})'.format(TOKEN_HEADER)}, 412

        result, status_code = validate_token(token)
        if status_code != 200:
            return {'Error' : result['Message']}, 403

        return f(*args, **kwargs)
    return decorated_function
