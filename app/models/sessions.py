from datetime import datetime
from app import db

class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    session_key = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    # İlişkiler
    user = db.relationship('User', backref='user_sessions', lazy=True)  # 'user' ile backref 'user_sessions' oldu

    def __repr__(self):
        return f'<Session {self.session_key}>'
