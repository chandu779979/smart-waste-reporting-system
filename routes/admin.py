from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SubmitField, StringField
from wtforms.validators import DataRequired, Length, Email
from extensions import db
from models.complaint import Complaint
from models.status_history import ComplaintStatusHistory
from utilities.helpers import admin_required
from utilities.notifications import send_complaint_updated_email, send_complaint_resolved_email

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ==========================================
# WTForms Definitions
# ==========================================

class UpdateStatusForm(FlaskForm):
    status = SelectField('Update Status', choices=[
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved')
    ], validators=[DataRequired()])
    comment = TextAreaField('Comment / Action Taken', validators=[DataRequired(), Length(min=5, message="Comment must be at least 5 characters long.")])
    submit = SubmitField('Update Status')

class MunicipalityContactForm(FlaskForm):
    contact_number = StringField('Public Contact Number', validators=[DataRequired(), Length(max=50)])
    contact_email = StringField('Public Contact Email', validators=[DataRequired(), Email(), Length(max=120)])
    office_address = TextAreaField('Office Address', validators=[DataRequired()])
    office_hours = StringField('Office Hours', validators=[DataRequired(), Length(max=150)])
    submit = SubmitField('Update Contact Profile')

# ==========================================
# Admin Routes
# ==========================================

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    municipality_id = current_user.municipality_id
    municipality_name = current_user.municipality.name
    
    # Paginated list of complaints for this municipality
    page = request.args.get('page', 1, type=int)
    pagination = Complaint.query.filter_by(municipality_id=municipality_id)\
        .order_by(Complaint.created_at.desc())\
        .paginate(page=page, per_page=15, error_out=False)
        
    complaints = pagination.items
    total_complaints = pagination.total
    
    # Calculate Dashboard Analytics Data (filtered by Admin's Municipality)
    all_municipality_complaints = Complaint.query.filter_by(municipality_id=municipality_id).all()
    
    # 1. Status count
    status_counts = {
        'Pending': sum(1 for c in all_municipality_complaints if c.status == 'Pending'),
        'In Progress': sum(1 for c in all_municipality_complaints if c.status == 'In Progress'),
        'Resolved': sum(1 for c in all_municipality_complaints if c.status == 'Resolved')
    }
    
    # 2. Waste Category count
    categories = ['Overflowing Bin', 'Garbage Pile', 'Plastic Waste', 'Construction Waste', 'Roadside Waste', 'Organic Waste', 'Others']
    category_counts = {cat: sum(1 for c in all_municipality_complaints if c.waste_category == cat) for cat in categories}
    
    # 3. Monthly complaints
    monthly_counts = {}
    for comp in sorted(all_municipality_complaints, key=lambda x: x.created_at):
        month_label = comp.created_at.strftime('%b %Y')
        monthly_counts[month_label] = monthly_counts.get(month_label, 0) + 1
        
    return render_template(
        'admin/dashboard.html',
        complaints=complaints,
        pagination=pagination,
        total_complaints=total_complaints,
        municipality_name=municipality_name,
        status_counts=status_counts,
        category_counts=category_counts,
        monthly_counts=monthly_counts
    )

@admin_bp.route('/complaint/<int:complaint_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def complaint_details(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Ensure admin only accesses complaints from their municipality
    if complaint.municipality_id != current_user.municipality_id:
        flash('Unauthorized access: this complaint does not belong to your municipality.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    form = UpdateStatusForm()
    
    if form.validate_on_submit():
        previous_status = complaint.status
        new_status = form.status.data
        comment_text = form.comment.data
        
        # Update complaint details
        complaint.status = new_status
        
        # Log status transition history
        history = ComplaintStatusHistory(
            complaint_id=complaint.id,
            previous_status=previous_status,
            new_status=new_status,
            comment=comment_text,
            updated_by_name=current_user.name
        )
        db.session.add(history)
        db.session.commit()
        
        # Send email notification to citizen (fails silently if Brevo not configured)
        citizen = complaint.citizen
        if new_status == 'Resolved':
            send_complaint_resolved_email(
                citizen.name, citizen.email, complaint.id, history.timestamp
            )
        else:
            send_complaint_updated_email(
                citizen.name, citizen.email, complaint.id,
                previous_status, new_status, history.timestamp,
                admin_remarks=comment_text
            )
        
        flash(f'Complaint status updated successfully from {previous_status} to {new_status}!', 'success')
        return redirect(url_for('admin.complaint_details', complaint_id=complaint.id))
        
    # Pre-populate form with current status on GET request
    if request.method == 'GET':
        form.status.data = complaint.status
        
    return render_template('admin/complaint_details.html', complaint=complaint, form=form)

@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@admin_required
def profile():
    municipality = current_user.municipality
    form = MunicipalityContactForm()
    
    if form.validate_on_submit():
        municipality.contact_number = form.contact_number.data
        municipality.contact_email = form.contact_email.data
        municipality.office_address = form.office_address.data
        municipality.office_hours = form.office_hours.data
        db.session.commit()
        
        flash('Municipality contact profile updated successfully!', 'success')
        return redirect(url_for('admin.profile'))
        
    if request.method == 'GET':
        form.contact_number.data = municipality.contact_number
        form.contact_email.data = municipality.contact_email
        form.office_address.data = municipality.office_address
        form.office_hours.data = municipality.office_hours
        
    return render_template('admin/profile.html', form=form, municipality=municipality)
