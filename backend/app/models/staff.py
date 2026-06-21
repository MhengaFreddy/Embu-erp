from ..extensions import db
from datetime import datetime

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    employee_number = db.Column(db.String(20), unique=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    designation = db.Column(db.String(100))
    date_joined = db.Column(db.Date)
    phone = db.Column(db.String(15))

    # HR relations
    leave_requests = db.relationship('LeaveRequest', backref='staff', lazy=True)
    salary_records = db.relationship('Salary', backref='staff', lazy=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
