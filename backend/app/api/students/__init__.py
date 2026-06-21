from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from ...models.students import Student
from ...models.users import User, Role
from ...extensions import db

students_bp = Blueprint('students', __name__)

# ── Profile endpoint for the logged‑in student ──
@students_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_my_profile():
    user_id = int(get_jwt_identity())               # user.id from token
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({'error': 'No student profile found for this user'}), 404

    return jsonify({
        'id': student.id,
        'user_id': student.user_id,
        'admission_number': student.admission_number,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'date_of_birth': str(student.date_of_birth) if student.date_of_birth else None,
        'gender': student.gender,
        'phone': student.phone,
        'enrollment_status': student.enrollment_status
    })

# ── List all students (admin/registrar) ──
@students_bp.route('/', methods=['GET'])
@jwt_required()
def get_students():
    students = Student.query.all()
    result = []
    for s in students:
        result.append({
            'id': s.id,
            'admission_number': s.admission_number,
            'first_name': s.first_name,
            'last_name': s.last_name,
            'enrollment_status': s.enrollment_status
        })
    return jsonify(result)

# ── Single student (by student table id) ──
@students_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_student(id):
    s = Student.query.get_or_404(id)
    return jsonify({
        'id': s.id,
        'admission_number': s.admission_number,
        'first_name': s.first_name,
        'last_name': s.last_name,
        'enrollment_status': s.enrollment_status
    })

# ── Create student ──
@students_bp.route('/', methods=['POST'])
@jwt_required()
def create_student():
    data = request.get_json()
    student_role = Role.query.filter_by(name='student').first()
    email = f"{data['admission_number'].lower()}@college.edu"
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 400

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
