from datetime import datetime
from app import db

class MindMap(db.Model):
    __tablename__ = 'mindmaps'

    map_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    style_id = db.Column(db.Integer, db.ForeignKey('styles.style_id'))

    # İlişkiler
    user = db.relationship('User', backref='mindmaps_owned', lazy=True)  # 'user' ile backref 'mindmaps_owned' oldu
    style = db.relationship('Style', backref='mindmaps_style', lazy=True)
    goals = db.relationship('Goal', backref='mindmap_relation', lazy=True, cascade='all, delete-orphan') 

    def __repr__(self):
        return f'<MindMap {self.title}>'
