from app import db

class Style(db.Model):
    __tablename__ = 'styles'

    style_id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(50))
    shape = db.Column(db.String(50))

    # İlişkiler
    mindmaps = db.relationship('MindMap', backref='style_of_map', lazy=True)

    def __repr__(self):
        return f'<Style {self.color}, {self.shape}>'
