from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True) 
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        # Şifreyi hashleyerek veritabanında sakla
        self.password = generate_password_hash(password)

    def check_password(self, password):
        # Girilen şifreyi kontrol et
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
