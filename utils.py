import os
import secrets
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename


def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_picture(form_picture, folder='profile'):
    """
    Save a picture to disk with a random filename
    Args:
        form_picture: FileStorage object from form
        folder: subfolder to save to ('profile', 'blog', 'product')
    Returns:
        filename: the saved filename
    """
    if not form_picture or not allowed_file(form_picture.filename):
        return None
    
    # Generate random filename
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext.lower()
    
    # Create folder path
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_path, exist_ok=True)
    
    picture_path = os.path.join(upload_path, picture_fn)
    
    # Resize image to save space
    img = Image.open(form_picture)
    img.thumbnail((800, 800), Image.Resampling.LANCZOS)
    img.save(picture_path, quality=85)
    
    return os.path.join(folder, picture_fn)


def delete_picture(filename):
    """Delete a picture from disk"""
    if filename:
        picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(picture_path):
            os.remove(picture_path)
