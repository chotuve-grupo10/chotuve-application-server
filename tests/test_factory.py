from app_server import create_app

def test_config():
	# TODO: esto se puede descomentar cuando en init no estemos tratando de hacer una op con la db
	# assert not create_app().testing
	assert create_app({'TESTING': True}).testing
	