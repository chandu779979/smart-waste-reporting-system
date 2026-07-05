from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from extensions import db, login_manager
from models.citizen import Citizen
from models.admin import Admin
from models.municipality import Municipality
from utilities.notifications import send_welcome_email

auth_bp = Blueprint('auth', __name__)

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('citizen:'):
        citizen_id = int(user_id.split(':')[1])
        return Citizen.query.get(citizen_id)
    elif user_id.startswith('admin:'):
        admin_id = int(user_id.split(':')[1])
        return Admin.query.get(admin_id)
    return None

# ==========================================
# WTForms Definitions
# ==========================================

class CitizenRegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=100)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register as Citizen')
    
    def validate_email(self, email):
        citizen = Citizen.query.filter_by(email=email.data).first()
        admin = Admin.query.filter_by(email=email.data).first()
        if citizen or admin:
            raise ValidationError('Email address is already in use.')

class CitizenLoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AdminRegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    municipality_id = SelectField('Select Municipality', coerce=int, validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=100)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register as Admin')
    
    def validate(self, extra_validators=None):
        # Call base validation (skip email because it has no validators)
        if not super().validate(extra_validators):
            return False
            
        # Get selected municipality
        municipality = Municipality.query.get(self.municipality_id.data)
        if not municipality:
            self.municipality_id.errors.append('Invalid municipality selection.')
            return False
            
        # Automatically map name to prefix: e.g. "Anantapur Municipality" -> "admin@anantapur.gov.in"
        prefix = municipality.name.lower().replace(" municipality", "").strip().replace(" ", "-")
        generated_email = f"admin@{prefix}.gov.in"
        self.email.data = generated_email
        
        # Check if email is already in use
        existing_citizen = Citizen.query.filter_by(email=generated_email).first()
        existing_admin = Admin.query.filter_by(email=generated_email).first()
        if existing_citizen or existing_admin:
            self.municipality_id.errors.append(f'An admin for {municipality.name} ({generated_email}) is already registered.')
            return False
            
        return True

class AdminLoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# ==========================================
# Authentication Routes
# ==========================================

@auth_bp.route('/register/citizen', methods=['GET', 'POST'])
def citizen_register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = CitizenRegisterForm()
    if form.validate_on_submit():
        citizen = Citizen(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data
        )
        citizen.set_password(form.password.data)
        db.session.add(citizen)
        db.session.commit()
        
        # Send welcome email notification (fails silently if SMTP not configured)
        send_welcome_email(citizen.name, citizen.email)
        
        flash('Citizen registration successful! Please log in.', 'success')
        return redirect(url_for('auth.citizen_login'))
        
    return render_template('auth/citizen_register.html', form=form)

@auth_bp.route('/login/citizen', methods=['GET', 'POST'])
def citizen_login():
    if current_user.is_authenticated:
        if getattr(current_user, 'is_citizen', False):
            return redirect(url_for('citizen.dashboard'))
        elif getattr(current_user, 'is_admin', False):
            return redirect(url_for('admin.dashboard'))
            
    form = CitizenLoginForm()
    if form.validate_on_submit():
        citizen = Citizen.query.filter_by(email=form.email.data).first()
        if citizen and citizen.check_password(form.password.data):
            login_user(citizen)
            flash(f'Welcome back, {citizen.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('citizen.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('auth/citizen_login.html', form=form)

@auth_bp.route('/register/admin', methods=['GET', 'POST'])
def admin_register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = AdminRegisterForm()
    # Dynamically populate municipalities list
    form.municipality_id.choices = [(m.id, m.name) for m in Municipality.query.order_by(Municipality.name).all()]
    
    if form.validate_on_submit():
        admin = Admin(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            municipality_id=form.municipality_id.data
        )
        admin.set_password(form.password.data)
        db.session.add(admin)
        db.session.commit()
        
        flash('Admin registration successful! Please log in.', 'success')
        return redirect(url_for('auth.admin_login'))
        
    return render_template('auth/admin_register.html', form=form)

@auth_bp.route('/login/admin', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        if getattr(current_user, 'is_citizen', False):
            return redirect(url_for('citizen.dashboard'))
        elif getattr(current_user, 'is_admin', False):
            return redirect(url_for('admin.dashboard'))
            
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            flash(f'Welcome back Admin, {admin.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('auth/admin_login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))
