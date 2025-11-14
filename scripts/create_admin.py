"""Create or update an admin user for the Agrifarma app.

Run this from the project root (PowerShell example):

    py scripts\create_admin.py

It will prompt for username, email and password. If the user exists it will update the role/password.
"""
import getpass
from app import create_app
from extensions import db
from models.user import User


def main():
    app = create_app()
    username = input('Admin username: ').strip()
    email = input('Admin email: ').strip()
    password = getpass.getpass('Admin password: ')
    if not username or not email or not password:
        print('username, email and password are required')
        return

    with app.app_context():
        user = User.query.filter((User.username == username) | (User.email == email)).first()
        if user:
            print(f'Updating existing user: {user.username} ({user.email})')
            user.username = username
            user.email = email
        else:
            user = User(username=username, email=email, role='admin')
            db.session.add(user)

        user.role = 'admin'
        user.set_password(password)
        db.session.commit()
        print(f'Admin user "{username}" created/updated successfully.')


if __name__ == '__main__':
    main()
