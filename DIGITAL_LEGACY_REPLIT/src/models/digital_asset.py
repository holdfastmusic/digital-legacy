from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class DigitalAsset(db.Model):
    __tablename__ = 'digital_assets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)  # social_media, email, cloud_storage, financial, etc.
    url = db.Column(db.String(500))
    username = db.Column(db.String(100))
    credentials_encrypted = db.Column(db.Text)  # Encrypted password/credentials
    instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('digital_assets', lazy=True))
    
    def __repr__(self):
        return f'<DigitalAsset {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'asset_type': self.asset_type,
            'url': self.url,
            'username': self.username,
            'instructions': self.instructions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

