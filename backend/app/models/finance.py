from ..extensions import db
from datetime import datetime, date

class FeeStructure(db.Model):
    __tablename__ = 'fee_structures'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'))
    total_amount = db.Column(db.Numeric(10,2))

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'))
    amount = db.Column(db.Numeric(10,2))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, partial, paid

    payments = db.relationship('Payment', backref='invoice', lazy=True)

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))
    amount = db.Column(db.Numeric(10,2))
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    method = db.Column(db.String(20))  # mpesa, bank, cash
    transaction_reference = db.Column(db.String(50))
    receipt_number = db.Column(db.String(30))

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(10,2))
    category = db.Column(db.String(50))
    date = db.Column(db.Date)

class Salary(db.Model):
    __tablename__ = 'salaries'
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    month = db.Column(db.String(7))  # YYYY-MM
    basic_pay = db.Column(db.Numeric(10,2))
    deductions = db.Column(db.Numeric(10,2))
    net_pay = db.Column(db.Numeric(10,2))

class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    leave_type = db.Column(db.String(30))  # sick, annual, etc.
    status = db.Column(db.String(20), default='pending')