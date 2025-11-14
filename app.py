import os
from flask import Flask
from config import Config
from extensions import db, login_manager


def create_app():
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_object(Config)

	# ensure instance folder exists
	try:
		os.makedirs(app.instance_path, exist_ok=True)
	except Exception:
		pass

	db.init_app(app)
	
	# import models BEFORE init_app so user_loader is registered
	from models.user import User
	from models.blog import Post, Comment, Like
	from models.product import Product
	
	login_manager.init_app(app)

	# register blueprints
	from routes.auth import auth_bp
	app.register_blueprint(auth_bp)

	# admin blueprint (admin panel)
	try:
		from routes.admin import admin_bp
		app.register_blueprint(admin_bp)
	except Exception:
		# admin blueprint may not exist during early development
		pass

	# blog blueprint
	try:
		from routes.blog import blog_bp
		app.register_blueprint(blog_bp)
	except Exception:
		# blog blueprint may not exist during early development
		pass

	# create database tables if they don't exist
	with app.app_context():
		db.create_all()

		# Ensure there is at least one admin user. Credentials can be provided via
		# environment variables: ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD.
		# If ADMIN_PASSWORD is not set, default easy password will be used.
		admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
		admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
		admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')

		# Only create/update admin if no admin exists yet
		from models.user import User
		existing_admin = User.query.filter_by(role='admin').first()
		if not existing_admin:
			user = User.query.filter((User.username == admin_username) | (User.email == admin_email)).first()

			if user:
				user.username = admin_username
				user.email = admin_email
				user.role = 'admin'
				user.set_password(admin_password)
				print(f"[setup] Updated existing user '{user.username}' to admin.")
				print(f"[setup] Admin credentials: Username='{admin_username}', Password='{admin_password}'")
			else:
				user = User(username=admin_username, email=admin_email, role='admin')
				user.set_password(admin_password)
				db.session.add(user)
				print(f"[setup] Created admin user '{admin_username}'.")
				print(f"[setup] Admin credentials: Username='{admin_username}', Password='{admin_password}'")

			db.session.commit()

	return app


if __name__ == '__main__':
	app = create_app()
	app.run(debug=True)
