from app import db

class MindMap(db.Model):
    __tablename__ = 'mindmaps'

    map_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    style_id = db.Column(db.Integer, db.ForeignKey('styles.style_id'))

    goals = db.relationship('Goal', backref='mindmap', lazy=True, cascade="all, delete")
    shared_mindmaps = db.relationship('SharedMindMap', backref='mindmap', lazy=True)

