from ..extensions import db
from datetime import datetime

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    admission_number = db.Column(db.String(20), unique=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    national_id = db.Column(db.String(30))
    phone = db.Column(db.String(15))
    photo_url = db.Column(db.Text)
    documents = db.Column(db.JSON)
    address = db.Column(db.Text)
    enrollment_status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    invoices = db.relationship('Invoice', backref='student', lazy=True)
    allocations = db.relationship('Allocation', backref='student', lazy=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
