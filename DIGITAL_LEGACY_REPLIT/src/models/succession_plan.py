from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class SuccessionPlan(db.Model):
    __tablename__ = 'succession_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trigger_days = db.Column(db.Integer, default=90)  # Days of inactivity before triggering
    status = db.Column(db.String(20), default='active')  # active, triggered, completed
    instructions = db.Column(db.Text)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('succession_plan', uselist=False))
    
    def __repr__(self):
        return f'<SuccessionPlan {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'trigger_days': self.trigger_days,
            'status': self.status,
            'instructions': self.instructions,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

