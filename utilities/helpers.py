from functools import wraps
from flask import abort, redirect, url_for, flash, current_app
from flask_login import current_user
import os
from werkzeug.utils import secure_filename
import uuid

def citizen_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in as a Citizen to access this page.", "warning")
            return redirect(url_for('auth.citizen_login'))
        if not getattr(current_user, 'is_citizen', False):
            flash("Access denied. Citizen role required.", "danger")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in as a Municipality Admin to access this page.", "warning")
            return redirect(url_for('auth.admin_login'))
        if not getattr(current_user, 'is_admin', False):
            flash("Access denied. Admin role required.", "danger")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_uploaded_image(file):
    if not file or file.filename == '':
        return None
    if not allowed_file(file.filename):
        return None
        
    filename = secure_filename(file.filename)
    # Generate unique filename using UUID
    file_ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)
    return unique_filename
