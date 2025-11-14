from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from extensions import db
from models.user import User
from models.blog import Post, Comment, Like
from forms.blog import PostForm, CommentForm
from flask_login import login_required, current_user
from datetime import datetime
from utils import save_picture, delete_picture

blog_bp = Blueprint('blog', __name__, template_folder='../templates/blog', url_prefix='/blog')


@blog_bp.route('/')
def list_posts():
    """List all blog posts (public, anyone can view)"""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('blog/posts.html', posts=posts)


@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create a new blog post (authenticated users only)"""
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id
        )
        
        # Handle image upload
        if form.post_image.data:
            picture_file = save_picture(form.post_image.data, folder='blog')
            post.post_image = picture_file
        
        db.session.add(post)
        db.session.commit()
        flash('✓ Post created successfully!', 'success')
        return redirect(url_for('blog.view_post', post_id=post.id))
    return render_template('blog/create.html', form=form)


@blog_bp.route('/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    """View a single blog post with comments"""
    post = Post.query.get_or_404(post_id)
    form = CommentForm() if current_user.is_authenticated else None
    
    if form and form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('✓ Comment posted!', 'success')
        return redirect(url_for('blog.view_post', post_id=post.id))
    
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()
    return render_template('blog/post_detail.html', post=post, comments=comments, form=form)


@blog_bp.route('/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    """Like/Unlike a blog post"""
    post = Post.query.get_or_404(post_id)
    
    # Check if user already liked this post
    existing_like = Like.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        db.session.commit()
        flash('✓ Post unliked.', 'info')
    else:
        # Like
        like = Like(post_id=post_id, user_id=current_user.id)
        db.session.add(like)
        db.session.commit()
        flash('✓ Post liked!', 'success')
    
    return redirect(url_for('blog.view_post', post_id=post_id))


@blog_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit a blog post (author or admin only)"""
    post = Post.query.get_or_404(post_id)
    
    # Check if user is author or admin
    if current_user.id != post.user_id and current_user.role != 'admin':
        abort(403)
    
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        
        # Handle image upload
        if form.post_image.data:
            # Delete old image if exists
            if post.post_image:
                delete_picture(post.post_image)
            # Save new image
            picture_file = save_picture(form.post_image.data, folder='blog')
            post.post_image = picture_file
        
        post.updated_at = datetime.utcnow()
        db.session.commit()
        flash('✓ Post updated successfully!', 'success')
        return redirect(url_for('blog.view_post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    
    return render_template('blog/edit.html', form=form, post=post)


@blog_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete a blog post (author or admin only)"""
    post = Post.query.get_or_404(post_id)
    
    # Check if user is author or admin
    if current_user.id != post.user_id and current_user.role != 'admin':
        abort(403)
    
    db.session.delete(post)
    db.session.commit()
    flash('✓ Post deleted.', 'info')
    return redirect(url_for('blog.list_posts'))


@blog_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Delete a comment (author or post author or admin only)"""
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    
    # Check if user is comment author, post author, or admin
    if (current_user.id != comment.user_id and 
        current_user.id != comment.post.user_id and 
        current_user.role != 'admin'):
        abort(403)
    
    db.session.delete(comment)
    db.session.commit()
    flash('✓ Comment deleted.', 'info')
    return redirect(url_for('blog.view_post', post_id=post_id))
