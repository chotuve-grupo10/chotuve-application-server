from app_server import token_functions

def test_decode_token_successfully():
    user_data = {'email' : 'test@test.com'}
    token = token_functions.generate_app_token(user_data)

    result, status_code = token_functions.validate_token(token)

    assert status_code == 200

def test_is_not_valid_token():
    result, status_code = token_functions.validate_token('testststs')

    assert status_code == 401
