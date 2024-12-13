from app import db
from datetime import datetime

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    session_key = db.Column(db.String(256), unique=True, nullable=False)  # Oturum anahtarı
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # Kullanıcı ID'si
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Oturum oluşturulma zamanı
    expires_at = db.Column(db.DateTime, nullable=True)  # Oturumun geçerlilik süresi
