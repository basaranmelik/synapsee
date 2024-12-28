from app import db

class Goal(db.Model):
    __tablename__ = 'goals'

    goal_id = db.Column(db.Integer, primary_key=True)
    map_id = db.Column(db.Integer, db.ForeignKey('mindmaps.map_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date)

    steps = db.relationship('Step', backref='goal', lazy=True)
