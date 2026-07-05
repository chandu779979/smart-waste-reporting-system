from extensions import db

class Municipality(db.Model):
    __tablename__ = 'municipalities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    
    contact_number = db.Column(db.String(50), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    office_address = db.Column(db.Text, nullable=True)
    office_hours = db.Column(db.String(150), nullable=True)
    
    # Relationships
    admins = db.relationship('Admin', back_populates='municipality', cascade='all, delete-orphan')
    complaints = db.relationship('Complaint', back_populates='municipality', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Municipality {self.name}>"
