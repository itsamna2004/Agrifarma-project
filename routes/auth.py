from flask import Blueprint, render_template, redirect, url_for, flash, request
from extensions import db
from models.user import User
from models.blog import Post
from models.product import Product
from forms.auth import RegistrationForm, LoginForm, ProfileForm
from forms.product import ProductForm
from flask_login import login_user, logout_user, login_required, current_user
from utils import save_picture, delete_picture

auth_bp = Blueprint('auth', __name__, template_folder='../templates')


@auth_bp.route('/')
def index():
    return render_template('home.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # check existing username/email
        if User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first():
            flash('Username or email already taken.', 'warning')
            return render_template('register.html', form=form)

        # First user becomes admin; subsequent users get their chosen role
        user_count = User.query.count()
        role = 'admin' if user_count == 0 else form.role.data
        user = User(username=form.username.data, email=form.email.data, role=role)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        if user_count == 0:
            flash('✓ You are the first user - admin rights granted!', 'success')
        else:
            flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        # allow login by username or email
        user = User.query.filter((User.username == form.username.data) | (User.email == form.username.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            # Redirect to profile completion if not complete
            if not user.profile_complete:
                return redirect(url_for('auth.complete_profile'))
            next_page = request.args.get('next')
            return redirect(next_page or url_for('auth.dashboard'))
        flash('Invalid username/email or password.', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/complete-profile', methods=['GET', 'POST'])
@login_required
def complete_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.bio = form.bio.data
        
        # Handle image upload
        if form.profile_image.data:
            # Delete old image if exists
            if current_user.profile_image:
                delete_picture(current_user.profile_image)
            # Save new image
            picture_file = save_picture(form.profile_image.data, folder='profile')
            current_user.profile_image = picture_file
        
        current_user.profile_complete = True
        db.session.commit()
        flash('Profile completed!', 'success')
        return redirect(url_for('auth.dashboard'))
    return render_template('complete_profile.html', form=form)


@auth_bp.route('/skip-profile')
@login_required
def skip_profile():
    current_user.profile_complete = True
    db.session.commit()
    flash('Profile skipped for now. You can complete it later.', 'info')
    return redirect(url_for('auth.dashboard'))


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    # show a minimal dashboard that surfaces the user's role
    return render_template('dashboard.html')


@auth_bp.route('/about')
def about():
    return render_template('about.html')


@auth_bp.route('/marketplace')
def marketplace():
    return render_template('marketplace.html')


@auth_bp.route('/forum')
def forum():
    return render_template('forum.html')


@auth_bp.route('/consultant')
def consultant():
    return render_template('consultant.html')


@auth_bp.route('/consultants')
def consultants_list():
    """List all registered consultants"""
    consultants = User.query.filter_by(role='consultant').all()
    return render_template('consultants_list.html', consultants=consultants)


@auth_bp.route('/products')
def products_list():
    """List all products"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    
    query = Product.query
    if category:
        query = query.filter_by(category=category)
    
    products = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=12)
    return render_template('products_list.html', products=products, selected_category=category)


@auth_bp.route('/discussions')
def discussions_list():
    """List all forum discussions"""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('discussions_list.html', posts=posts)


@auth_bp.route('/profile')
@login_required
def profile():
    """View current user profile"""
    return render_template('profile.html')


@auth_bp.route('/list-product', methods=['GET', 'POST'])
@login_required
def list_product():
    """List a new product (farmers and vendors only)"""
    if current_user.role not in ['farmer', 'vendor']:
        flash('Only farmers and vendors can list products.', 'warning')
        return redirect(url_for('auth.marketplace'))
    
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            category=form.category.data,
            description=form.description.data,
            price=form.price.data,
            quantity=form.quantity.data,
            location=form.location.data,
            contact=form.contact.data,
            user_id=current_user.id
        )
        
        # Handle image upload
        if form.product_image.data:
            picture_file = save_picture(form.product_image.data, folder='product')
            product.product_image = picture_file
        
        db.session.add(product)
        db.session.commit()
        flash('✓ Product listed successfully!', 'success')
        return redirect(url_for('auth.products_list'))
    
    return render_template('list_product.html', form=form)
