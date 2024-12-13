from app import db

class SharedMindMap(db.Model):
    __tablename__ = 'shared_mindmaps'

    shared_id = db.Column(db.Integer, primary_key=True)
    map_id = db.Column(db.Integer, db.ForeignKey('mindmaps.map_id'), nullable=False)
    shared_with_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    permission_level = db.Column(db.String(50), nullable=False)
