from datetime import datetime
from extensions import db

class Complaint(db.Model):
    __tablename__ = 'complaints'
    
    id = db.Column(db.Integer, primary_key=True)
    citizen_id = db.Column(db.Integer, db.ForeignKey('citizens.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    waste_category = db.Column(db.String(50), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    
    # Geolocation fields
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    
    # Association
    municipality_id = db.Column(db.Integer, db.ForeignKey('municipalities.id'), nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False) # 'Pending', 'In Progress', 'Resolved'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    citizen = db.relationship('Citizen', back_populates='complaints')
    municipality = db.relationship('Municipality', back_populates='complaints')
    status_history = db.relationship('ComplaintStatusHistory', back_populates='complaint', order_by='ComplaintStatusHistory.timestamp.desc()', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Complaint {self.id} - {self.title} ({self.status})>"
