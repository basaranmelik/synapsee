from datetime import datetime
from app import db

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    log_id = db.Column(db.Integer, primary_key=True)
    action_datetime = db.Column(db.DateTime, default=datetime.utcnow)
    action_type = db.Column(db.String(20), nullable=False)  # INSERT, UPDATE, DELETE gibi
    table_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)  # Kullanıcıyı ilişkilendirdik
    record_id = db.Column(db.Integer, nullable=False)
    old_data = db.Column(db.JSON)  # Eski veri
    new_data = db.Column(db.JSON)  # Yeni veri
    session_info = db.Column(db.JSON)  # Oturum bilgisi

    # İlişkiler
    user = db.relationship('User', backref='activity_logs', lazy=True)  # 'user' ile backref 'activity_logs' oldu

    def __repr__(self):
        return f'<ActivityLog {self.log_id}>'
