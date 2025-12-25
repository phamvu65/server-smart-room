from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    fullname = db.Column(db.String(100)) 
    phone = db.Column(db.String(15))     
    dob = db.Column(db.Date)             
class WorkSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Float)
    warning_count = db.Column(db.Integer, default=0)
    avg_temp = db.Column(db.Float)
    avg_humidity = db.Column(db.Float)
    
    user = db.relationship('User', backref=db.backref('sessions', lazy=True))