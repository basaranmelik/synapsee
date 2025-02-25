from app import db

class Step(db.Model):
    __tablename__ = 'steps'

    step_id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.goal_id'), nullable=False)
    description = db.Column(db.Text, nullable=False)

    # İlişkiler
    goal = db.relationship('Goal', backref='steps_of_goal', lazy=True)  # 'goal' yerine 'steps_of_goal'

    def __repr__(self):
        return f'<Step {self.description}>'
