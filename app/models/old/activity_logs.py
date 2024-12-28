from app import db

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    log_id = db.Column(db.Integer, primary_key=True)
    action_datetime = db.Column(db.DateTime, nullable=False)
    action_type = db.Column(db.String(20), nullable=False)
    table_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    old_data = db.Column(db.JSON, nullable=True)
    new_data = db.Column(db.JSON, nullable=True)
    session_info = db.Column(db.JSON, nullable=True)
