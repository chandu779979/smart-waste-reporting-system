from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length
from extensions import db
from models.complaint import Complaint
from models.municipality import Municipality
from models.status_history import ComplaintStatusHistory
from utilities.helpers import citizen_required, save_uploaded_image
from utilities.notifications import send_complaint_submitted_email

citizen_bp = Blueprint('citizen', __name__, url_prefix='/citizen')

# ==========================================
# WTForms Definitions
# ==========================================

class ComplaintForm(FlaskForm):
    title = StringField('Complaint Title', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Description', validators=[DataRequired()])
    waste_category = SelectField('Waste Category', choices=[
        ('Overflowing Bin', 'Overflowing Bin'),
        ('Garbage Pile', 'Garbage Pile'),
        ('Plastic Waste', 'Plastic Waste'),
        ('Construction Waste', 'Construction Waste'),
        ('Roadside Waste', 'Roadside Waste'),
        ('Organic Waste', 'Organic Waste'),
        ('Others', 'Others')
    ], validators=[DataRequired()])
    image = FileField('Upload Image (jpg, jpeg, png, max 5MB)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    latitude = StringField('Latitude', validators=[DataRequired(message="Latitude is required. Select on map or enter manually.")])
    longitude = StringField('Longitude', validators=[DataRequired(message="Longitude is required. Select on map or enter manually.")])
    address = StringField('Selected Address', validators=[DataRequired(message="Address is required. Select on map or enter manually.")])
    municipality_id = SelectField('Municipality', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit Complaint')

class CitizenProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    submit = SubmitField('Update Profile')

# ==========================================
# Citizen Routes
# ==========================================

@citizen_bp.route('/dashboard')
@login_required
@citizen_required
def dashboard():
    # Fetch complaints reported by the current citizen
    page = request.args.get('page', 1, type=int)
    pagination = Complaint.query.filter_by(citizen_id=current_user.id)\
        .order_by(Complaint.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    complaints = pagination.items
    total_complaints = pagination.total
    
    # Calculate Dashboard Analytics Data (Python side for simplicity and accuracy)
    all_citizen_complaints = Complaint.query.filter_by(citizen_id=current_user.id).all()
    
    # Find unique municipalities the citizen has reported complaints to
    reported_municipalities = []
    seen_ids = set()
    for c in all_citizen_complaints:
        if c.municipality_id not in seen_ids:
            seen_ids.add(c.municipality_id)
            reported_municipalities.append(c.municipality)
            
    # 1. Status count
    status_counts = {
        'Pending': sum(1 for c in all_citizen_complaints if c.status == 'Pending'),
        'In Progress': sum(1 for c in all_citizen_complaints if c.status == 'In Progress'),
        'Resolved': sum(1 for c in all_citizen_complaints if c.status == 'Resolved')
    }
    
    # 2. Waste Category count
    categories = ['Overflowing Bin', 'Garbage Pile', 'Plastic Waste', 'Construction Waste', 'Roadside Waste', 'Organic Waste', 'Others']
    category_counts = {cat: sum(1 for c in all_citizen_complaints if c.waste_category == cat) for cat in categories}
    
    # 3. Monthly complaints (last 6 months dynamically grouped)
    monthly_counts = {}
    for comp in sorted(all_citizen_complaints, key=lambda x: x.created_at):
        month_label = comp.created_at.strftime('%b %Y')
        monthly_counts[month_label] = monthly_counts.get(month_label, 0) + 1
        
    return render_template(
        'citizen/dashboard.html',
        complaints=complaints,
        pagination=pagination,
        total_complaints=total_complaints,
        status_counts=status_counts,
        category_counts=category_counts,
        monthly_counts=monthly_counts,
        reported_municipalities=reported_municipalities
    )

@citizen_bp.route('/complaint/submit', methods=['GET', 'POST'])
@login_required
@citizen_required
def submit_complaint():
    form = ComplaintForm()
    # Populate municipalities list dynamically
    form.municipality_id.choices = [(m.id, m.name) for m in Municipality.query.order_by(Municipality.name).all()]
    
    if form.validate_on_submit():
        image_filename = None
        if form.image.data:
            image_filename = save_uploaded_image(form.image.data)
            
        # Create complaint
        complaint = Complaint(
            citizen_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            waste_category=form.waste_category.data,
            image_path=image_filename,
            latitude=float(form.latitude.data),
            longitude=float(form.longitude.data),
            address=form.address.data,
            municipality_id=form.municipality_id.data,
            status='Pending'
        )
        db.session.add(complaint)
        db.session.flush() # Flush to get the complaint ID
        
        # Log initial status change in history
        history = ComplaintStatusHistory(
            complaint_id=complaint.id,
            previous_status=None,
            new_status='Pending',
            comment='Complaint submitted successfully.',
            updated_by_name=current_user.name
        )
        db.session.add(history)
        db.session.commit()
        
        # Send email confirmation to citizen (fails silently if Brevo not configured)
        municipality = Municipality.query.get(complaint.municipality_id)
        send_complaint_submitted_email(
            current_user.name,
            current_user.email,
            complaint.id,
            municipality.name if municipality else 'N/A',
            complaint.waste_category,
            complaint.created_at
        )
        
        flash('Your complaint has been submitted successfully!', 'success')
        return redirect(url_for('citizen.dashboard'))
        
    return render_template('citizen/complaint_form.html', form=form)

@citizen_bp.route('/complaint/<int:complaint_id>')
@login_required
@citizen_required
def complaint_details(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Ensure citizens can only see their own complaints
    if complaint.citizen_id != current_user.id:
        flash('Unauthorized access to complaint details.', 'danger')
        return redirect(url_for('citizen.dashboard'))
        
    return render_template('citizen/complaint_details.html', complaint=complaint)

@citizen_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@citizen_required
def profile():
    form = CitizenProfileForm()
    if request.method == 'GET':
        form.name.data = current_user.name
        form.phone.data = current_user.phone
        
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.phone = form.phone.data
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('citizen.profile'))
        
    return render_template('citizen/profile.html', form=form)
