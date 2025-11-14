import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	
	# Image upload configuration
	UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
	MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
	ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
	
	# Ensure upload folder exists
	os.makedirs(UPLOAD_FOLDER, exist_ok=True)

