from app import create_app
from models.user import User

app = create_app()
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f'✓ Admin found: {admin.username}')
        print(f'✓ Admin email: {admin.email}')
        print(f'✓ Admin role: {admin.role}')
        print(f'✓ Password hash: {admin.password_hash}')
        # Test password check
        result = admin.check_password('admin123')
        print(f'Password check result: {result}')
        if result:
            print('✅ Password check PASSED!')
        else:
            print('❌ Password check FAILED!')
    else:
        print('❌ Admin user not found')
        users = User.query.all()
        print(f'All users in database: {[u.username for u in users]}')
