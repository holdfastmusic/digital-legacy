from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class AssetAssignment(db.Model):
    __tablename__ = 'asset_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('digital_assets.id'), nullable=False)
    beneficiary_id = db.Column(db.Integer, db.ForeignKey('beneficiaries.id'), nullable=False)
    instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    asset = db.relationship('DigitalAsset', backref=db.backref('assignments', lazy=True))
    beneficiary = db.relationship('Beneficiary', backref=db.backref('assignments', lazy=True))
    
    def __repr__(self):
        return f'<AssetAssignment {self.asset_id} -> {self.beneficiary_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'beneficiary_id': self.beneficiary_id,
            'instructions': self.instructions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

