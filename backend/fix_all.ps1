# models\students.py
@"
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
"@ | Set-Content app\models\students.py

# models\staff.py
@"
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

    leave_requests = db.relationship('LeaveRequest', backref='staff', lazy=True)
    salary_records = db.relationship('Salary', backref='staff', lazy=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
"@ | Set-Content app\models\staff.py

# models\academic.py
@"
from ..extensions import db
from datetime import date

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    code = db.Column(db.String(10), unique=True)
    courses = db.relationship('Course', backref='department', lazy=True)
    staff_members = db.relationship('Staff', backref='department', lazy=True)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    code = db.Column(db.String(10), unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    units = db.relationship('Unit', backref='course', lazy=True)
    fee_structures = db.relationship('FeeStructure', backref='course', lazy=True)

class Semester(db.Model):
    __tablename__ = 'semesters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    academic_year = db.Column(db.String(9))
    units = db.relationship('Unit', backref='semester', lazy=True)
    enrollments = db.relationship('Enrollment', backref='semester', lazy=True)

class Unit(db.Model):
    __tablename__ = 'units'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    code = db.Column(db.String(10), unique=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'))
    credit_hours = db.Column(db.Integer)
    enrollments = db.relationship('Enrollment', backref='unit', lazy=True)
    exams = db.relationship('Exam', backref='unit', lazy=True)
    timetable_entries = db.relationship('Timetable', backref='unit', lazy=True)

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'))
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'))
    enrollment_date = db.Column(db.Date, default=date.today)

class Timetable(db.Model):
    __tablename__ = 'timetables'
    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'))
    lecturer_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    day_of_week = db.Column(db.SmallInteger)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    room = db.Column(db.String(20))

class Exam(db.Model):
    __tablename__ = 'exams'
    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'))
    exam_date = db.Column(db.Date)
    exam_type = db.Column(db.String(20))
    max_marks = db.Column(db.Numeric(5,2))
    results = db.relationship('Result', backref='exam', lazy=True)

class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'))
    marks = db.Column(db.Numeric(5,2))
    grade = db.Column(db.String(2))
    gpa_points = db.Column(db.Numeric(3,2))
"@ | Set-Content app\models\academic.py

# models\finance.py
@"
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
    status = db.Column(db.String(20), default='pending')
    payments = db.relationship('Payment', backref='invoice', lazy=True)

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))
    amount = db.Column(db.Numeric(10,2))
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    method = db.Column(db.String(20))
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
    month = db.Column(db.String(7))
    basic_pay = db.Column(db.Numeric(10,2))
    deductions = db.Column(db.Numeric(10,2))
    net_pay = db.Column(db.Numeric(10,2))

class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    leave_type = db.Column(db.String(30))
    status = db.Column(db.String(20), default='pending')
"@ | Set-Content app\models\finance.py

# models\library.py
@"
from ..extensions import db
from datetime import date

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20))
    title = db.Column(db.String(200))
    author = db.Column(db.String(100))
    barcode = db.Column(db.String(50), unique=True)
    total_copies = db.Column(db.Integer)
    available_copies = db.Column(db.Integer)

class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    borrow_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    return_date = db.Column(db.Date, nullable=True)
    fine = db.Column(db.Numeric(10,2), default=0)
"@ | Set-Content app\models\library.py

# models\hostel.py
@"
from ..extensions import db

class Hostel(db.Model):
    __tablename__ = 'hostels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    block = db.Column(db.String(10))
    rooms = db.relationship('Room', backref='hostel', lazy=True)

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    hostel_id = db.Column(db.Integer, db.ForeignKey('hostels.id'))
    room_number = db.Column(db.String(10))
    capacity = db.Column(db.Integer)
    occupied_beds = db.Column(db.Integer, default=0)
    fee_per_semester = db.Column(db.Numeric(10,2))
    allocations = db.relationship('Allocation', backref='room', lazy=True)

class Allocation(db.Model):
    __tablename__ = 'allocations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date, nullable=True)
"@ | Set-Content app\models\hostel.py

# models\inventory.py
@"
from ..extensions import db
from datetime import datetime

class Asset(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(50))
    serial_number = db.Column(db.String(50), unique=True)
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')

class PurchaseRequest(db.Model):
    __tablename__ = 'purchase_requests'
    id = db.Column(db.Integer, primary_key=True)
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    item_description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100))
"@ | Set-Content app\models\inventory.py

# models\communication.py
@"
from ..extensions import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text)
    channel = db.Column(db.String(20))
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='sent')

class EmailTemplate(db.Model):
    __tablename__ = 'email_templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    subject = db.Column(db.String(200))
    body_html = db.Column(db.Text)
"@ | Set-Content app\models\communication.py

# api\finance\__init__.py
@"
from flask import Blueprint, request
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.finance import Invoice, Payment, Expense
from ...extensions import db

finance_bp = Blueprint('finance', __name__)
api = Api(finance_bp, doc='/docs')
finance_ns = Namespace('finance', description='Financial operations')
api.add_namespace(finance_ns, path='/')

@finance_ns.route('/invoices')
class InvoiceList(Resource):
    @jwt_required()
    @role_required('finance_officer', 'super_admin', 'registrar')
    def get(self):
        invoices = Invoice.query.all()
        return [{'id': inv.id, 'student_id': inv.student_id, 'amount': float(inv.amount), 'status': inv.status} for inv in invoices]

    @jwt_required()
    @role_required('finance_officer', 'super_admin')
    def post(self):
        data = request.json
        invoice = Invoice(**data)
        db.session.add(invoice)
        db.session.commit()
        return {'message': 'Invoice created', 'id': invoice.id}, 201

@finance_ns.route('/payments')
class PaymentResource(Resource):
    @jwt_required()
    @role_required('finance_officer', 'super_admin')
    def get(self):
        payments = Payment.query.all()
        return [{'id': p.id, 'invoice_id': p.invoice_id, 'amount': float(p.amount), 'method': p.method, 'payment_date': str(p.payment_date)} for p in payments]

    @jwt_required()
    @role_required('finance_officer', 'super_admin')
    def post(self):
        data = request.json
        payment = Payment(**data)
        db.session.add(payment)
        invoice = Invoice.query.get(data['invoice_id'])
        total_paid = sum(p.amount for p in invoice.payments) + payment.amount
        invoice.status = 'paid' if total_paid >= invoice.amount else 'partial'
        db.session.commit()
        return {'message': 'Payment recorded', 'receipt': payment.receipt_number}, 201

@finance_ns.route('/expenses')
class ExpenseList(Resource):
    @jwt_required()
    @role_required('finance_officer', 'super_admin')
    def get(self):
        expenses = Expense.query.all()
        return [{'id': e.id, 'description': e.description, 'amount': float(e.amount), 'category': e.category, 'date': str(e.date)} for e in expenses]
"@ | Set-Content app\api\finance\__init__.py

# api\academic\__init__.py
@"
from flask import Blueprint, request
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.academic import Department, Course, Semester, Unit, Enrollment, Timetable, Exam, Result
from ...extensions import db

academic_bp = Blueprint('academic', __name__)
api = Api(academic_bp, doc='/docs')
academic_ns = Namespace('academic', description='Academic management')
api.add_namespace(academic_ns, path='/')

def obj_to_dict(obj, cols):
    return {col: str(getattr(obj, col)) if getattr(obj, col) and not isinstance(getattr(obj, col), (int, float)) else getattr(obj, col) for col in cols}

@academic_ns.route('/departments')
class DeptList(Resource):
    @jwt_required()
    def get(self):
        depts = Department.query.all()
        return [obj_to_dict(d, ['id', 'name', 'code']) for d in depts]

@academic_ns.route('/courses')
class CourseList(Resource):
    @jwt_required()
    def get(self):
        courses = Course.query.all()
        return [obj_to_dict(c, ['id', 'name', 'code', 'department_id']) for c in courses]

@academic_ns.route('/units')
class UnitList(Resource):
    @jwt_required()
    def get(self):
        units = Unit.query.all()
        return [obj_to_dict(u, ['id', 'name', 'code', 'course_id', 'semester_id', 'credit_hours']) for u in units]

@academic_ns.route('/timetable')
class TimetableList(Resource):
    @jwt_required()
    def get(self):
        entries = Timetable.query.all()
        return [{'id': e.id, 'unit_id': e.unit_id, 'lecturer_id': e.lecturer_id, 'day_of_week': e.day_of_week, 'start_time': str(e.start_time), 'end_time': str(e.end_time), 'room': e.room} for e in entries]

@academic_ns.route('/exams')
class ExamList(Resource):
    @jwt_required()
    def get(self):
        exams = Exam.query.all()
        return [obj_to_dict(e, ['id', 'unit_id', 'exam_date', 'exam_type', 'max_marks']) for e in exams]

@academic_ns.route('/results')
class ResultList(Resource):
    @jwt_required()
    def get(self):
        results = Result.query.all()
        return [obj_to_dict(r, ['id', 'student_id', 'exam_id', 'marks', 'grade', 'gpa_points']) for r in results]
"@ | Set-Content app\api\academic\__init__.py

# api\hr\__init__.py
@"
from flask import Blueprint, request
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.staff import Staff
from ...models.finance import LeaveRequest, Salary
from ...extensions import db

hr_bp = Blueprint('hr', __name__)
api = Api(hr_bp, doc='/docs')
hr_ns = Namespace('hr', description='Human Resources')
api.add_namespace(hr_ns, path='/')

@hr_ns.route('/staff')
class StaffList(Resource):
    @jwt_required()
    @role_required('hr_manager', 'super_admin')
    def get(self):
        staff = Staff.query.all()
        return [{'id': s.id, 'employee_number': s.employee_number, 'first_name': s.first_name, 'last_name': s.last_name, 'designation': s.designation, 'phone': s.phone} for s in staff]

@hr_ns.route('/leave-requests')
class LeaveList(Resource):
    @jwt_required()
    @role_required('hr_manager', 'super_admin', 'lecturer')
    def get(self):
        leaves = LeaveRequest.query.all()
        return [{'id': l.id, 'staff_id': l.staff_id, 'start_date': str(l.start_date), 'end_date': str(l.end_date), 'leave_type': l.leave_type, 'status': l.status} for l in leaves]

@hr_ns.route('/payroll')
class PayrollList(Resource):
    @jwt_required()
    @role_required('hr_manager', 'super_admin')
    def get(self):
        salaries = Salary.query.all()
        return [{'id': s.id, 'staff_id': s.staff_id, 'month': s.month, 'basic_pay': float(s.basic_pay), 'deductions': float(s.deductions), 'net_pay': float(s.net_pay)} for s in salaries]
"@ | Set-Content app\api\hr\__init__.py

# api\library\__init__.py
@"
from flask import Blueprint, request
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.library import Book, Loan
from ...extensions import db
from datetime import date, timedelta

library_bp = Blueprint('library', __name__)
api = Api(library_bp, doc='/docs')
library_ns = Namespace('library', description='Library management')
api.add_namespace(library_ns, path='/')

@library_ns.route('/books')
class BookList(Resource):
    @jwt_required()
    def get(self):
        books = Book.query.all()
        return [{'id': b.id, 'isbn': b.isbn, 'title': b.title, 'author': b.author, 'barcode': b.barcode, 'total_copies': b.total_copies, 'available_copies': b.available_copies} for b in books]

    @jwt_required()
    @role_required('librarian', 'super_admin')
    def post(self):
        data = request.json
        book = Book(**data)
        db.session.add(book)
        db.session.commit()
        return {'message': 'Book added', 'id': book.id}, 201

@library_ns.route('/loans')
class LoanList(Resource):
    @jwt_required()
    def get(self):
        loans = Loan.query.all()
        return [{'id': l.id, 'book_id': l.book_id, 'user_id': l.user_id, 'borrow_date': str(l.borrow_date), 'due_date': str(l.due_date), 'return_date': str(l.return_date) if l.return_date else None, 'fine': float(l.fine)} for l in loans]

    @jwt_required()
    @role_required('librarian', 'super_admin')
    def post(self):
        data = request.json
        book = Book.query.get(data['book_id'])
        if book.available_copies < 1:
            return {'message': 'Book not available'}, 400
        loan = Loan(book_id=data['book_id'], user_id=data['user_id'], borrow_date=date.today(), due_date=date.today() + timedelta(days=14))
        book.available_copies -= 1
        db.session.add(loan)
        db.session.commit()
        return {'message': 'Book loaned', 'id': loan.id}, 201
"@ | Set-Content app\api\library\__init__.py

# api\hostel\__init__.py
@"
from flask import Blueprint, request
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.hostel import Hostel, Room, Allocation
from ...extensions import db
from datetime import date

hostel_bp = Blueprint('hostel', __name__)
api = Api(hostel_bp, doc='/docs')
hostel_ns = Namespace('hostel', description='Hostel management')
api.add_namespace(hostel_ns, path='/')

@hostel_ns.route('/rooms')
class RoomList(Resource):
    @jwt_required()
    def get(self):
        rooms = Room.query.all()
        return [{'id': r.id, 'hostel_id': r.hostel_id, 'room_number': r.room_number, 'capacity': r.capacity, 'occupied_beds': r.occupied_beds, 'fee_per_semester': float(r.fee_per_semester)} for r in rooms]

@hostel_ns.route('/allocations')
class AllocationList(Resource):
    @jwt_required()
    def get(self):
        allocs = Allocation.query.all()
        return [{'id': a.id, 'student_id': a.student_id, 'room_id': a.room_id, 'start_date': str(a.start_date), 'end_date': str(a.end_date) if a.end_date else None} for a in allocs]

    @jwt_required()
    @role_required('hostel_manager', 'super_admin')
    def post(self):
        data = request.json
        room = Room.query.get(data['room_id'])
        if room.occupied_beds >= room.capacity:
            return {'message': 'Room full'}, 400
        alloc = Allocation(student_id=data['student_id'], room_id=data['room_id'], start_date=date.today())
        room.occupied_beds += 1
        db.session.add(alloc)
        db.session.commit()
        return {'message': 'Room allocated'}, 201
"@ | Set-Content app\api\hostel\__init__.py

# api\inventory\__init__.py
@"
from flask import Blueprint, request
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.inventory import Asset, PurchaseRequest, Supplier
from ...extensions import db

inventory_bp = Blueprint('inventory', __name__)
api = Api(inventory_bp, doc='/docs')
inventory_ns = Namespace('inventory', description='Inventory & Procurement')
api.add_namespace(inventory_ns, path='/')

@inventory_ns.route('/assets')
class AssetList(Resource):
    @jwt_required()
    def get(self):
        assets = Asset.query.all()
        return [{'id': a.id, 'name': a.name, 'category': a.category, 'serial_number': a.serial_number, 'location': a.location, 'status': a.status} for a in assets]

@inventory_ns.route('/suppliers')
class SupplierList(Resource):
    @jwt_required()
    def get(self):
        suppliers = Supplier.query.all()
        return [{'id': s.id, 'name': s.name, 'contact_person': s.contact_person, 'phone': s.phone, 'email': s.email} for s in suppliers]

@inventory_ns.route('/purchase-requests')
class PurchaseRequestList(Resource):
    @jwt_required()
    def get(self):
        prs = PurchaseRequest.query.all()
        return [{'id': p.id, 'requested_by': p.requested_by, 'item_description': p.item_description, 'status': p.status, 'created_at': str(p.created_at)} for p in prs]
"@ | Set-Content app\api\inventory\__init__.py

# api\communication\__init__.py
@"
from flask import Blueprint, request
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.communication import Notification
from ...extensions import db
from datetime import datetime

comm_bp = Blueprint('communication', __name__)
api = Api(comm_bp, doc='/docs')
comm_ns = Namespace('communication', description='Communication & Notifications')
api.add_namespace(comm_ns, path='/')

@comm_ns.route('/send')
class SendMessage(Resource):
    @jwt_required()
    @role_required('super_admin', 'registrar', 'principal')
    def post(self):
        data = request.json
        try:
            user_id = int(data['recipient'])
        except ValueError:
            from ...models.users import User
            user = User.query.filter_by(email=data['recipient']).first()
            if not user:
                return {'message': 'Recipient not found'}, 404
            user_id = user.id
        notif = Notification(user_id=user_id, message=data['message'], channel=data['channel'], sent_at=datetime.utcnow(), status='sent')
        db.session.add(notif)
        db.session.commit()
        return {'message': 'Notification sent'}, 201

@comm_ns.route('/notifications')
class NotificationHistory(Resource):
    @jwt_required()
    def get(self):
        notifs = Notification.query.order_by(Notification.sent_at.desc()).limit(100).all()
        return [{'id': n.id, 'user_id': n.user_id, 'message': n.message, 'channel': n.channel, 'sent_at': str(n.sent_at), 'status': n.status} for n in notifs]
"@ | Set-Content app\api\communication\__init__.py

# api\dashboard\__init__.py
@"
from flask import Blueprint
from flask_restx import Api, Namespace, Resource
from flask_jwt_extended import jwt_required
from ...models.students import Student
from ...models.finance import Payment
from ...models.staff import Staff
from ...models.library import Book
from ...extensions import db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)
api = Api(dashboard_bp, doc='/docs')
dashboard_ns = Namespace('dashboard', description='Dashboard statistics')
api.add_namespace(dashboard_ns, path='/')

@dashboard_ns.route('/stats')
class DashboardStats(Resource):
    @jwt_required()
    def get(self):
        total_students = Student.query.count()
        total_fees = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).scalar()
        total_staff = Staff.query.count()
        total_books = Book.query.count()
        return {
            'total_students': total_students,
            'fee_collected': float(total_fees),
            'total_staff': total_staff,
            'total_books': total_books,
            'enrollment_labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'enrollment_data': [5, 10, 15, 20, 25],
            'revenue_labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'revenue_data': [5000, 10000, 15000, 20000, 25000]
        }, 200
"@ | Set-Content app\api\dashboard\__init__.py

# services\mpesa.py & grading.py
@"
import requests
from base64 import b64encode
from datetime import datetime
from flask import current_app

def get_access_token():
    consumer_key = current_app.config['MPESA_CONSUMER_KEY']
    consumer_secret = current_app.config['MPESA_CONSUMER_SECRET']
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(auth_url, auth=(consumer_key, consumer_secret))
    return response.json().get('access_token')

def stk_push(phone_number, amount, account_reference):
    access_token = get_access_token()
    shortcode = current_app.config['MPESA_SHORTCODE']
    passkey = current_app.config['MPESA_PASSKEY']
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://yourdomain.com/api/mpesa/callback",
        "AccountReference": account_reference,
        "TransactionDesc": "Fee Payment"
    }
    response = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
    return response.json()
"@ | Set-Content app\services\mpesa.py

@"
def calculate_grade_and_gpa(marks, max_marks=100):
    percent = (marks / max_marks) * 100
    if percent >= 70:
        return 'A', 4.0
    elif percent >= 60:
        return 'B', 3.0
    elif percent >= 50:
        return 'C', 2.0
    elif percent >= 40:
        return 'D', 1.0
    else:
        return 'F', 0.0
"@ | Set-Content app\services\grading.py

# schemas\student.py
@"
from ..extensions import ma
from ..models.students import Student

class StudentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Student
        load_instance = True
        include_fk = True

student_schema = StudentSchema()
students_schema = StudentSchema(many=True)
"@ | Set-Content app\schemas\student.py

Write-Host "All files have been created successfully."