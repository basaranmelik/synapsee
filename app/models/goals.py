from app import db

class Goal(db.Model):
    __tablename__ = 'goals'

    goal_id = db.Column(db.Integer, primary_key=True)
    map_id = db.Column(db.Integer, db.ForeignKey('mindmaps.map_id'), nullable=True)
    title = db.Column(db.String(255), nullable=False)

    # İlişkiler
    mindmap = db.relationship('MindMap', backref='goals_in_map', lazy=True)  # 'goal' yerine 'goals_in_map'
    steps = db.relationship('Step', backref='goal_for_step', lazy=True, cascade='all, delete-orphan')  # 'goal' yerine 'goal_for_step'

    def __repr__(self):
        return f'<Goal {self.title}>'
