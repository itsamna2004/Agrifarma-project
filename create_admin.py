#!/usr/bin/env python
"""Script to create admin user"""
from app import create_app, db
from models.user import User

app = create_app()

with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        print(f"Admin user already exists")
        print(f"Username: {admin.username}")
        print(f"Email: {admin.email}")
        # Update password to admin123
        admin.set_password('admin123')
        db.session.commit()
        print("Password updated to: admin123")
    else:
        # Create new admin
        admin = User(username='admin', email='admin@example.com', role='admin', profile_complete=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")
        print("Username: admin")
        print("Email: admin@example.com")
        print("Password: admin123")
    
    # Verify
    test_user = User.query.filter_by(username='admin').first()
    if test_user and test_user.check_password('admin123'):
        print("\n✅ LOGIN TEST PASSED - Admin can login!")
    else:
        print("\n❌ LOGIN TEST FAILED - There's an issue")
