from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class Citizen(UserMixin, db.Model):
    __tablename__ = 'citizens'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    complaints = db.relationship('Complaint', back_populates='citizen', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def get_id(self):
        # Override to prevent conflicts between Citizen and Admin IDs in Flask-Login
        return f"citizen:{self.id}"
        
    @property
    def is_citizen(self):
        return True
        
    @property
    def is_admin(self):
        return False

    def __repr__(self):
        return f"<Citizen {self.email}>"
