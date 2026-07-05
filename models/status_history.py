from datetime import datetime
from extensions import db

class ComplaintStatusHistory(db.Model):
    __tablename__ = 'complaint_status_history'
    
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    previous_status = db.Column(db.String(20), nullable=True)
    new_status = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    updated_by_name = db.Column(db.String(100), nullable=False) # Name of user who updated it
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    complaint = db.relationship('Complaint', back_populates='status_history')
    
    def __repr__(self):
        return f"<ComplaintStatusHistory {self.complaint_id}: {self.previous_status} -> {self.new_status}>"
