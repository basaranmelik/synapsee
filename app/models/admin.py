from datetime import datetime
from app import db

class Admin(db.Model):
    __tablename__ = 'admin'

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # İlişki
    user = db.relationship('User', backref=db.backref('admin', uselist=False))

    def __repr__(self):
        return f'<Admin {self.name}>'
