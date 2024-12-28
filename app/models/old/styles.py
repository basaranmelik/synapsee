from app import db

class Style(db.Model):
    __tablename__ = 'styles'

    style_id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(50))
    shape = db.Column(db.String(50))

    mindmaps = db.relationship('MindMap', backref='style', lazy=True)
