from ..extensions import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text)
    channel = db.Column(db.String(20))  # email, sms
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='sent')

class EmailTemplate(db.Model):
    __tablename__ = 'email_templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    subject = db.Column(db.String(200))
    body_html = db.Column(db.Text)
