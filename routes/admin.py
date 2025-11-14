from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from extensions import db
from models.user import User
from models.blog import Post, Comment, Like
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin', url_prefix='/admin')


def admin_required():
    if not current_user.is_authenticated or current_user.role != 'admin':
        abort(403)


@admin_bp.route('/')
@login_required
def index():
    admin_required()
    
    # Get statistics
    total_users = User.query.count()
    admin_users = User.query.filter_by(role='admin').count()
    consultant_users = User.query.filter_by(role='consultant').count()
    farmer_users = User.query.filter_by(role='farmer').count()
    vendor_users = User.query.filter_by(role='vendor').count()
    customer_users = User.query.filter_by(role='customer').count()
    
    total_posts = Post.query.count()
    total_comments = Comment.query.count()
    total_likes = Like.query.count()
    
    # Get recent users
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    
    # Get recent posts
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    
    # Prepare role distribution for chart
    role_stats = {
        'admin': admin_users,
        'consultant': consultant_users,
        'farmer': farmer_users,
        'vendor': vendor_users,
        'customer': customer_users
    }
    
    stats = {
        'total_users': total_users,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_likes': total_likes,
        'role_stats': role_stats
    }
    
    return render_template('admin/dashboard.html', stats=stats, recent_users=recent_users, recent_posts=recent_posts)


@admin_bp.route('/users')
@login_required
def users():
    admin_required()
    users = User.query.order_by(User.id.asc()).all()
    roles = ['admin', 'customer', 'consultant', 'farmer', 'vendor']
    return render_template('admin/users.html', users=users, roles=roles)


@admin_bp.route('/user/<int:user_id>/role', methods=['POST'])
@login_required
def change_role(user_id):
    admin_required()
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    if new_role not in ('admin', 'customer', 'consultant', 'farmer', 'vendor'):
        flash('Invalid role', 'danger')
        return redirect(url_for('admin.users'))
    user.role = new_role
    db.session.commit()
    flash(f"Updated role for {user.username} to {new_role}", 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    admin_required()
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete yourself.', 'warning')
        return redirect(url_for('admin.users'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.', 'info')
    return redirect(url_for('admin.users'))


@admin_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    admin_required()
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role')
        password = request.form.get('password')

        if not username or not email:
            flash('Username and email are required.', 'warning')
            return redirect(url_for('admin.edit_user', user_id=user.id))

        user.username = username
        user.email = email
        if role in ('admin', 'customer', 'consultant', 'farmer', 'vendor'):
            user.role = role

        if password:
            user.set_password(password)

        db.session.commit()
        flash('User updated.', 'success')
        return redirect(url_for('admin.users'))

    roles = ['admin', 'customer', 'consultant', 'farmer', 'vendor']
    return render_template('admin/edit.html', user=user, roles=roles)
