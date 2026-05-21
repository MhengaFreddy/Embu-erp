from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.staff import Staff
from ...models.academic import Unit, Timetable, Exam, Result, Enrollment
from ...models.students import Student
from ...models.users import User
from ...extensions import db
from ...utils.decorators import role_required

lecturer_bp = Blueprint('lecturer', __name__)

# ── Get units assigned to the logged‑in lecturer ──
@lecturer_bp.route('/my-units', methods=['GET'])
@jwt_required()
@role_required('lecturer')
def my_units():
    user_id = int(get_jwt_identity())
    staff = Staff.query.filter_by(user_id=user_id).first()
    if not staff:
        return jsonify({'error': 'Lecturer profile not found'}), 404

    # Units where the lecturer is assigned in the timetable
    timetable_entries = Timetable.query.filter_by(lecturer_id=staff.id).all()
    unit_ids = list(set(e.unit_id for e in timetable_entries))
    units = Unit.query.filter(Unit.id.in_(unit_ids)).all() if unit_ids else []

    result = []
    for u in units:
        entries = Timetable.query.filter_by(lecturer_id=staff.id, unit_id=u.id).all()
        result.append({
            'unit_id': u.id,
            'unit_name': u.name,
            'unit_code': u.code,
            'schedule': [{
                'day': e.day_of_week,
                'start': str(e.start_time),
                'end': str(e.end_time),
                'room': e.room
            } for e in entries]
        })
    return jsonify(result)

# ── Get students enrolled in a specific unit (for results entry) ──
@lecturer_bp.route('/units/<int:unit_id>/students', methods=['GET'])
@jwt_required()
@role_required('lecturer')
def unit_students(unit_id):
    enrollments = Enrollment.query.filter_by(unit_id=unit_id).all()
    student_ids = [e.student_id for e in enrollments]
    students = Student.query.filter(Student.id.in_(student_ids)).all()
    return jsonify([{
        'student_id': s.id,
        'admission_number': s.admission_number,
        'name': f"{s.first_name} {s.last_name}"
    } for s in students])

# ── Submit a result ──
@lecturer_bp.route('/results', methods=['POST'])
@jwt_required()
@role_required('lecturer')
def submit_result():
    data = request.get_json()
    # data: { exam_id, student_id, marks }
    from ...services.grading import calculate_grade_and_gpa
    exam = Exam.query.get(data['exam_id'])
    if not exam:
        return jsonify({'error': 'Exam not found'}), 404

    grade, gpa = calculate_grade_and_gpa(data['marks'], float(exam.max_marks))
    result = Result(
        student_id=data['student_id'],
        exam_id=data['exam_id'],
        marks=data['marks'],
        grade=grade,
        gpa_points=gpa
    )
    db.session.add(result)
    db.session.commit()
    return jsonify({'message': 'Result saved', 'grade': grade}), 201