from datetime import datetime
from app import db

class SharedMindmap(db.Model):
    __tablename__ = 'shared_mindmaps'

    shared_id = db.Column(db.Integer, primary_key=True)
    map_id = db.Column(db.Integer, db.ForeignKey('mindmaps.map_id'), nullable=False)
    shared_with_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    # İlişkiler
    mindmap = db.relationship('MindMap', backref='shared_mindmaps', lazy=True)
    user = db.relationship('User', backref='shared_with_user', lazy=True)

    def __repr__(self):
        return f'<SharedMindmap {self.shared_id}>'
