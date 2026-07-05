from flask import Blueprint, render_template, current_app
from models.municipality import Municipality
from models.complaint import Complaint
from extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Show statistics summary on landing page
    total_complaints = Complaint.query.count()
    resolved_complaints = Complaint.query.filter_by(status='Resolved').count()
    municipalities_count = Municipality.query.count()
    
    return render_template(
        'main/index.html',
        total_complaints=total_complaints,
        resolved_complaints=resolved_complaints,
        municipalities_count=municipalities_count
    )

@main_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('main/404.html'), 404

@main_bp.app_context_processor
def inject_google_maps_key():
    return dict(google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY'])
