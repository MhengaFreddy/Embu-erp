#!/bin/bash
set -e

# =========================================================================
# Self‑repair: recreate ALL critical Python files from known‑good content
# =========================================================================

mkdir -p /app/app/api/auth
mkdir -p /app/app/api/finance
mkdir -p /app/app/api/students
mkdir -p /app/app/api/academic
mkdir -p /app/app/api/hr
mkdir -p /app/app/api/library
mkdir -p /app/app/api/hostel
mkdir -p /app/app/api/inventory
mkdir -p /app/app/api/communication
mkdir -p /app/app/api/dashboard
mkdir -p /app/app/api/lecturer
mkdir -p /app/app/api/users

# --- auth/__init__.py ---
cat > /app/app/api/auth/__init__.py << 'EOF'
from flask import Blueprint, request, jsonify
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from ...models.users import User, Role
from ...extensions import db

auth_bp = Blueprint('auth', __name__)
api = Api(auth_bp, doc='/docs')
auth_ns = Namespace('auth', description='Authentication operations')
api.add_namespace(auth_ns, path='/')

login_model = auth_ns.model('Login', {'email': fields.String(required=True), 'password': fields.String(required=True)})
register_model = auth_ns.model('Register', {'email': fields.String(required=True), 'password': fields.String(required=True), 'role': fields.String(required=True)})

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        data = request.json
        user = User.query.filter_by(email=data['email']).first()
        if not user or not check_password_hash(user.password_hash, data['password']):
            return {'message': 'Invalid credentials'}, 401
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        return {'access_token': access_token, 'refresh_token': refresh_token, 'user': user.to_dict()}, 200

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    def post(self):
        data = request.json
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already registered'}, 400
        role = Role.query.filter_by(name=data['role']).first()
        if not role:
            return {'message': 'Invalid role'}, 400
        hashed_pw = generate_password_hash(data['password'])
        new_user = User(email=data['email'], password_hash=hashed_pw, role_id=role.id)
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User registered successfully'}, 201

@auth_ns.route('/refresh')
class RefreshToken(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        return {'access_token': new_access_token}, 200
EOF

# --- finance/__init__.py ---
cat > /app/app/api/finance/__init__.py << 'EOF'
from flask import Blueprint, request
from flask_restx import Api, Namespace, Resource
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
    @role_required('finance_officer', 'super_admin', 'registrar', 'principal')
    def get(self):
        invoices = Invoice.query.all()
        return [{'id': inv.id, 'student_id': inv.student_id, 'amount': float(inv.amount), 'status': inv.status} for inv in invoices]

@finance_ns.route('/payments')
class PaymentResource(Resource):
    @jwt_required()
    @role_required('finance_officer', 'super_admin', 'registrar', 'principal')
    def get(self):
        payments = Payment.query.all()
        return [{'id': p.id, 'invoice_id': p.invoice_id, 'amount': float(p.amount), 'method': p.method, 'payment_date': str(p.payment_date)} for p in payments]

@finance_ns.route('/expenses')
class ExpenseList(Resource):
    @jwt_required()
    @role_required('finance_officer', 'super_admin', 'registrar', 'principal')
    def get(self):
        expenses = Expense.query.all()
        return [{'id': e.id, 'description': e.description, 'amount': float(e.amount), 'category': e.category, 'date': str(e.date)} for e in expenses]
EOF

# --- students/__init__.py (UPDATED with invoices + pay) ---
cat > /app/app/api/students/__init__.py << 'EOF'
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from ...models.students import Student
from ...models.users import User, Role
from ...models.academic import Enrollment
from ...models.finance import Invoice, Payment
from ...extensions import db
from datetime import datetime

students_bp = Blueprint('students', __name__)

# ── Profile endpoint ──
@students_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_my_profile():
    user_id = int(get_jwt_identity())
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({'error': 'No student profile found'}), 404

    programme = None
    enrollment = Enrollment.query.filter_by(student_id=student.id).first()
    if enrollment:
        unit = enrollment.unit
        if unit and unit.course:
            programme = unit.course.name

    return jsonify({
        'id': student.id,
        'admission_number': student.admission_number,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'date_of_birth': str(student.date_of_birth) if student.date_of_birth else None,
        'gender': student.gender,
        'phone': student.phone,
        'address': student.address,
        'enrollment_status': student.enrollment_status,
        'programme': programme or 'Not assigned'
    })

# ── Financial summary ──
@students_bp.route('/finances', methods=['GET'])
@jwt_required()
def get_my_finances():
    user_id = int(get_jwt_identity())
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    invoices = Invoice.query.filter_by(student_id=student.id).all()
    total_billed = sum(float(inv.amount) for inv in invoices)
    total_paid = 0.0
    for inv in invoices:
        total_paid += sum(float(p.amount) for p in inv.payments)
    balance = total_billed - total_paid

    return jsonify({
        'total_billed': total_billed,
        'total_paid': total_paid,
        'balance': balance
    })

# ── List student invoices ──
@students_bp.route('/invoices', methods=['GET'])
@jwt_required()
def get_my_invoices():
    user_id = int(get_jwt_identity())
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    invoices = Invoice.query.filter_by(student_id=student.id).all()
    result = []
    for inv in invoices:
        paid = sum(float(p.amount) for p in inv.payments)
        result.append({
            'id': inv.id,
            'semester_id': inv.semester_id,
            'amount': float(inv.amount),
            'due_date': str(inv.due_date),
            'status': inv.status,
            'paid': paid,
            'balance': float(inv.amount) - paid
        })
    return jsonify(result)

# ── Pay an invoice ──
@students_bp.route('/pay', methods=['POST'])
@jwt_required()
def pay_invoice():
    user_id = int(get_jwt_identity())
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    data = request.get_json()
    invoice_id = data.get('invoice_id')
    amount = float(data.get('amount', 0))

    invoice = Invoice.query.get(invoice_id)
    if not invoice or invoice.student_id != student.id:
        return jsonify({'error': 'Invalid invoice'}), 404

    if amount <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400

    payment = Payment(
        invoice_id=invoice.id,
        amount=amount,
        method='mpesa',
        transaction_reference=f"TEST{datetime.utcnow().timestamp()}",
        payment_date=datetime.utcnow()
    )
    db.session.add(payment)

    total_paid = sum(float(p.amount) for p in invoice.payments) + amount
    invoice.status = 'paid' if total_paid >= float(invoice.amount) else 'partial'
    db.session.commit()

    return jsonify({'message': 'Payment successful', 'paid': amount}), 201

# ── List all students (admin) ──
@students_bp.route('/', methods=['GET'])
@jwt_required()
def get_students():
    students = Student.query.all()
    return jsonify([{
        'id': s.id, 'admission_number': s.admission_number,
        'first_name': s.first_name, 'last_name': s.last_name,
        'enrollment_status': s.enrollment_status
    } for s in students])

# ── Create student (admin) ──
@students_bp.route('/', methods=['POST'])
@jwt_required()
def create_student():
    data = request.get_json()
    student_role = Role.query.filter_by(name='student').first()
    email = f"{data['admission_number'].lower()}@embucollege.ac.ke"
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    user = User(
        email=email,
        password_hash=generate_password_hash('student123'),
        role_id=student_role.id
    )
    db.session.add(user)
    db.session.flush()
    student = Student(
        user_id=user.id,
        admission_number=data['admission_number'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        date_of_birth=data.get('date_of_birth'),
        phone=data.get('phone'),
        enrollment_status='active'
    )
    db.session.add(student)
    db.session.commit()
    return jsonify({'message': 'Student created', 'student_id': student.id, 'email': email, 'default_password': 'student123'}), 201
EOF

# --- academic/__init__.py (minimal) ---
cat > /app/app/api/academic/__init__.py << 'EOF'
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ...models.academic import Department, Course, Unit, Timetable, Exam, Result

academic_bp = Blueprint('academic', __name__)

@academic_bp.route('/departments', methods=['GET'])
@jwt_required()
def get_departments():
    depts = Department.query.all()
    return jsonify([{'id': d.id, 'name': d.name, 'code': d.code} for d in depts])

@academic_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():
    courses = Course.query.all()
    return jsonify([{'id': c.id, 'name': c.name, 'code': c.code, 'department_id': c.department_id} for c in courses])

@academic_bp.route('/units', methods=['GET'])
@jwt_required()
def get_units():
    units = Unit.query.all()
    return jsonify([{'id': u.id, 'name': u.name, 'code': u.code, 'course_id': u.course_id, 'semester_id': u.semester_id, 'credit_hours': u.credit_hours} for u in units])
EOF

# --- hr/__init__.py ---
cat > /app/app/api/hr/__init__.py << 'EOF'
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.staff import Staff
from ...models.finance import LeaveRequest, Salary

hr_bp = Blueprint('hr', __name__)

@hr_bp.route('/staff', methods=['GET'])
@jwt_required()
@role_required('hr_manager', 'super_admin', 'principal', 'registrar')
def get_staff():
    staff = Staff.query.all()
    return jsonify([{'id': s.id, 'employee_number': s.employee_number, 'first_name': s.first_name, 'last_name': s.last_name, 'designation': s.designation, 'phone': s.phone} for s in staff])

@hr_bp.route('/leave-requests', methods=['GET'])
@jwt_required()
@role_required('hr_manager', 'super_admin', 'lecturer', 'principal')
def get_leave_requests():
    leaves = LeaveRequest.query.all()
    return jsonify([{'id': l.id, 'staff_id': l.staff_id, 'start_date': str(l.start_date), 'end_date': str(l.end_date), 'leave_type': l.leave_type, 'status': l.status} for l in leaves])

@hr_bp.route('/payroll', methods=['GET'])
@jwt_required()
@role_required('hr_manager', 'super_admin', 'principal')
def get_payroll():
    salaries = Salary.query.all()
    return jsonify([{'id': s.id, 'staff_id': s.staff_id, 'month': s.month, 'basic_pay': float(s.basic_pay), 'deductions': float(s.deductions), 'net_pay': float(s.net_pay)} for s in salaries])
EOF

# --- library/__init__.py ---
cat > /app/app/api/library/__init__.py << 'EOF'
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ...models.library import Book, Loan

library_bp = Blueprint('library', __name__)

@library_bp.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    books = Book.query.all()
    return jsonify([{'id': b.id, 'isbn': b.isbn, 'title': b.title, 'author': b.author, 'barcode': b.barcode, 'total_copies': b.total_copies, 'available_copies': b.available_copies} for b in books])

@library_bp.route('/loans', methods=['GET'])
@jwt_required()
def get_loans():
    loans = Loan.query.all()
    return jsonify([{'id': l.id, 'book_id': l.book_id, 'user_id': l.user_id, 'borrow_date': str(l.borrow_date), 'due_date': str(l.due_date), 'return_date': str(l.return_date) if l.return_date else None, 'fine': float(l.fine)} for l in loans])
EOF

# --- hostel/__init__.py ---
cat > /app/app/api/hostel/__init__.py << 'EOF'
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ...models.hostel import Room, Allocation

hostel_bp = Blueprint('hostel', __name__)

@hostel_bp.route('/rooms', methods=['GET'])
@jwt_required()
def get_rooms():
    rooms = Room.query.all()
    return jsonify([{'id': r.id, 'hostel_id': r.hostel_id, 'room_number': r.room_number, 'capacity': r.capacity, 'occupied_beds': r.occupied_beds, 'fee_per_semester': float(r.fee_per_semester)} for r in rooms])

@hostel_bp.route('/allocations', methods=['GET'])
@jwt_required()
def get_allocations():
    allocs = Allocation.query.all()
    return jsonify([{'id': a.id, 'student_id': a.student_id, 'room_id': a.room_id, 'start_date': str(a.start_date), 'end_date': str(a.end_date) if a.end_date else None} for a in allocs])
EOF

# --- inventory/__init__.py ---
cat > /app/app/api/inventory/__init__.py << 'EOF'
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ...models.inventory import Asset, Supplier, PurchaseRequest

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/assets', methods=['GET'])
@jwt_required()
def get_assets():
    assets = Asset.query.all()
    return jsonify([{'id': a.id, 'name': a.name, 'category': a.category, 'serial_number': a.serial_number, 'location': a.location, 'status': a.status} for a in assets])

@inventory_bp.route('/suppliers', methods=['GET'])
@jwt_required()
def get_suppliers():
    suppliers = Supplier.query.all()
    return jsonify([{'id': s.id, 'name': s.name, 'contact_person': s.contact_person, 'phone': s.phone, 'email': s.email} for s in suppliers])

@inventory_bp.route('/purchase-requests', methods=['GET'])
@jwt_required()
def get_purchase_requests():
    prs = PurchaseRequest.query.all()
    return jsonify([{'id': p.id, 'requested_by': p.requested_by, 'item_description': p.item_description, 'status': p.status, 'created_at': str(p.created_at)} for p in prs])
EOF

# --- communication/__init__.py ---
cat > /app/app/api/communication/__init__.py << 'EOF'
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ...models.communication import Notification
from ...extensions import db
from datetime import datetime

comm_bp = Blueprint('communication', __name__)

@comm_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    data = request.get_json()
    notif = Notification(user_id=data.get('recipient'), message=data.get('message'), channel=data.get('channel', 'email'), sent_at=datetime.utcnow(), status='sent')
    db.session.add(notif)
    db.session.commit()
    return jsonify({'message': 'Notification sent'}), 201

@comm_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    notifs = Notification.query.order_by(Notification.sent_at.desc()).limit(100).all()
    return jsonify([{'id': n.id, 'user_id': n.user_id, 'message': n.message, 'channel': n.channel, 'sent_at': str(n.sent_at), 'status': n.status} for n in notifs])
EOF

# --- dashboard/__init__.py ---
cat > /app/app/api/dashboard/__init__.py << 'EOF'
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ...models.students import Student
from ...models.finance import Payment
from ...models.staff import Staff
from ...models.library import Book
from ...extensions import db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    return jsonify({
        'total_students': Student.query.count(),
        'fee_collected': float(db.session.query(func.coalesce(func.sum(Payment.amount), 0)).scalar()),
        'total_staff': Staff.query.count(),
        'total_books': Book.query.count(),
        'enrollment_labels': ['Jan','Feb','Mar','Apr','May'],
        'enrollment_data': [5,10,15,20,25],
        'revenue_labels': ['Jan','Feb','Mar','Apr','May'],
        'revenue_data': [5000,10000,15000,20000,25000]
    })
EOF

# --- lecturer/__init__.py ---
cat > /app/app/api/lecturer/__init__.py << 'EOF'
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.staff import Staff
from ...models.academic import Timetable, Unit

lecturer_bp = Blueprint('lecturer', __name__)

@lecturer_bp.route('/my-units', methods=['GET'])
@jwt_required()
def my_units():
    user_id = int(get_jwt_identity())
    staff = Staff.query.filter_by(user_id=user_id).first()
    if not staff:
        return jsonify([])
    entries = Timetable.query.filter_by(lecturer_id=staff.id).all()
    unit_ids = list(set(e.unit_id for e in entries))
    units = Unit.query.filter(Unit.id.in_(unit_ids)).all()
    result = []
    for u in units:
        result.append({'unit_id': u.id, 'unit_name': u.name, 'unit_code': u.code})
    return jsonify(result)
EOF

# --- users/__init__.py ---
cat > /app/app/api/users/__init__.py << 'EOF'
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ...models.users import User
from ...utils.decorators import role_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('super_admin', 'principal')
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'email': u.email, 'role': u.role.name if u.role else 'N/A', 'is_active': u.is_active, 'last_login': str(u.last_login) if u.last_login else None, 'created_at': str(u.created_at)} for u in users])
EOF

# =========================================================================
# Normal startup
# =========================================================================
export FLASK_APP=run.py
python seed.py
exec python run.py