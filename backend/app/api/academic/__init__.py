from flask import Blueprint, request, jsonify
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.academic import Department, Course, Semester, Unit, Enrollment, Timetable, Exam, Result
from ...models.students import Student
from ...extensions import db

academic_bp = Blueprint('academic', __name__)
api = Api(academic_bp, doc='/docs')
academic_ns = Namespace('academic', description='Academic operations')
api.add_namespace(academic_ns, path='/')

# ---------- Models ----------
department_model = academic_ns.model('Department', {
    'name': fields.String(required=True),
    'code': fields.String(required=True)
})
course_model = academic_ns.model('Course', {
    'name': fields.String(required=True),
    'code': fields.String(required=True),
    'department_id': fields.Integer(required=True)
})
unit_model = academic_ns.model('Unit', {
    'name': fields.String(required=True),
    'code': fields.String(required=True),
    'course_id': fields.Integer(required=True),
    'semester_id': fields.Integer(required=True),
    'credit_hours': fields.Integer(required=True)
})
timetable_model = academic_ns.model('Timetable', {
    'unit_id': fields.Integer(required=True),
    'lecturer_id': fields.Integer(required=True),
    'day_of_week': fields.Integer(required=True, min=0, max=6),
    'start_time': fields.String(required=True),
    'end_time': fields.String(required=True),
    'room': fields.String(required=True)
})
exam_model = academic_ns.model('Exam', {
    'unit_id': fields.Integer(required=True),
    'exam_date': fields.Date(required=True),
    'exam_type': fields.String(required=True),
    'max_marks': fields.Float(required=True)
})
result_model = academic_ns.model('Result', {
    'student_id': fields.Integer(required=True),
    'exam_id': fields.Integer(required=True),
    'marks': fields.Float(required=True)
})

def obj_to_dict(obj, cols):
    return {col: str(getattr(obj, col)) if getattr(obj, col) is not None else None for col in cols}

# ---------- Departments ----------
@academic_ns.route('/departments')
class DepartmentList(Resource):
    @jwt_required()
    def get(self):
        depts = Department.query.all()
        return [obj_to_dict(d, ['id', 'name', 'code']) for d in depts]

    @jwt_required()
    @role_required('registrar', 'super_admin')
    @academic_ns.expect(department_model)
    def post(self):
        data = request.json
        dept = Department(name=data['name'], code=data['code'])
        db.session.add(dept)
        db.session.commit()
        return obj_to_dict(dept, ['id', 'name', 'code']), 201

@academic_ns.route('/departments/<int:id>')
class DepartmentDetail(Resource):
    @jwt_required()
    @role_required('registrar', 'super_admin')
    def put(self, id):
        dept = Department.query.get_or_404(id)
        data = request.json
        if 'name' in data: dept.name = data['name']
        if 'code' in data: dept.code = data['code']
        db.session.commit()
        return obj_to_dict(dept, ['id', 'name', 'code'])

    @jwt_required()
    @role_required('super_admin')
    def delete(self, id):
        dept = Department.query.get_or_404(id)
        db.session.delete(dept)
        db.session.commit()
        return {'message': 'Department deleted'}, 200

# ---------- Courses ----------
@academic_ns.route('/courses')
class CourseList(Resource):
    @jwt_required()
    def get(self):
        courses = Course.query.all()
        return [obj_to_dict(c, ['id', 'name', 'code', 'department_id']) for c in courses]

    @jwt_required()
    @role_required('registrar', 'super_admin')
    @academic_ns.expect(course_model)
    def post(self):
        data = request.json
        course = Course(name=data['name'], code=data['code'], department_id=data['department_id'])
        db.session.add(course)
        db.session.commit()
        return obj_to_dict(course, ['id', 'name', 'code', 'department_id']), 201

@academic_ns.route('/courses/<int:id>')
class CourseDetail(Resource):
    @jwt_required()
    @role_required('registrar', 'super_admin')
    def put(self, id):
        course = Course.query.get_or_404(id)
        data = request.json
        if 'name' in data: course.name = data['name']
        if 'code' in data: course.code = data['code']
        if 'department_id' in data: course.department_id = data['department_id']
        db.session.commit()
        return obj_to_dict(course, ['id', 'name', 'code', 'department_id'])

    @jwt_required()
    @role_required('super_admin')
    def delete(self, id):
        course = Course.query.get_or_404(id)
        db.session.delete(course)
        db.session.commit()
        return {'message': 'Course deleted'}, 200

# ---------- Units ----------
@academic_ns.route('/units')
class UnitList(Resource):
    @jwt_required()
    def get(self):
        units = Unit.query.all()
        return [obj_to_dict(u, ['id', 'name', 'code', 'course_id', 'semester_id', 'credit_hours']) for u in units]

    @jwt_required()
    @role_required('registrar', 'super_admin')
    @academic_ns.expect(unit_model)
    def post(self):
        data = request.json
        unit = Unit(**data)
        db.session.add(unit)
        db.session.commit()
        return obj_to_dict(unit, ['id', 'name', 'code', 'course_id', 'semester_id', 'credit_hours']), 201

@academic_ns.route('/units/<int:id>')
class UnitDetail(Resource):
    @jwt_required()
    @role_required('registrar', 'super_admin')
    def put(self, id):
        unit = Unit.query.get_or_404(id)
        data = request.json
        for key in ['name', 'code', 'course_id', 'semester_id', 'credit_hours']:
            if key in data:
                setattr(unit, key, data[key])
        db.session.commit()
        return obj_to_dict(unit, ['id', 'name', 'code', 'course_id', 'semester_id', 'credit_hours'])

    @jwt_required()
    @role_required('super_admin')
    def delete(self, id):
        unit = Unit.query.get_or_404(id)
        db.session.delete(unit)
        db.session.commit()
        return {'message': 'Unit deleted'}, 200

# ---------- Timetable ----------
@academic_ns.route('/timetable')
class TimetableList(Resource):
    @jwt_required()
    def get(self):
        entries = Timetable.query.all()
        result = []
        for e in entries:
            d = obj_to_dict(e, ['id', 'unit_id', 'lecturer_id', 'day_of_week', 'room'])
            d['start_time'] = str(e.start_time)
            d['end_time'] = str(e.end_time)
            result.append(d)
        return result

    @jwt_required()
    @role_required('registrar', 'super_admin')
    @academic_ns.expect(timetable_model)
    def post(self):
        data = request.json
        tt = Timetable(**data)
        db.session.add(tt)
        db.session.commit()
        return obj_to_dict(tt, ['id', 'unit_id', 'lecturer_id', 'day_of_week', 'room']), 201

@academic_ns.route('/timetable/<int:id>')
class TimetableDetail(Resource):
    @jwt_required()
    @role_required('registrar', 'super_admin')
    def put(self, id):
        tt = Timetable.query.get_or_404(id)
        data = request.json
        for key in ['unit_id', 'lecturer_id', 'day_of_week', 'start_time', 'end_time', 'room']:
            if key in data:
                setattr(tt, key, data[key])
        db.session.commit()
        return obj_to_dict(tt, ['id', 'unit_id', 'lecturer_id', 'day_of_week', 'room'])

    @jwt_required()
    @role_required('super_admin')
    def delete(self, id):
        tt = Timetable.query.get_or_404(id)
        db.session.delete(tt)
        db.session.commit()
        return {'message': 'Timetable entry deleted'}, 200

# ---------- Exams ----------
@academic_ns.route('/exams')
class ExamList(Resource):
    @jwt_required()
    def get(self):
        exams = Exam.query.all()
        return [obj_to_dict(e, ['id', 'unit_id', 'exam_date', 'exam_type', 'max_marks']) for e in exams]

    @jwt_required()
    @role_required('registrar', 'super_admin')
    @academic_ns.expect(exam_model)
    def post(self):
        data = request.json
        exam = Exam(**data)
        db.session.add(exam)
        db.session.commit()
        return obj_to_dict(exam, ['id', 'unit_id', 'exam_date', 'exam_type', 'max_marks']), 201

@academic_ns.route('/exams/<int:id>')
class ExamDetail(Resource):
    @jwt_required()
    @role_required('registrar', 'super_admin')
    def put(self, id):
        exam = Exam.query.get_or_404(id)
        data = request.json
        for key in ['unit_id', 'exam_date', 'exam_type', 'max_marks']:
            if key in data:
                setattr(exam, key, data[key])
        db.session.commit()
        return obj_to_dict(exam, ['id', 'unit_id', 'exam_date', 'exam_type', 'max_marks'])

    @jwt_required()
    @role_required('super_admin')
    def delete(self, id):
        exam = Exam.query.get_or_404(id)
        db.session.delete(exam)
        db.session.commit()
        return {'message': 'Exam deleted'}, 200

# ---------- Results ----------
@academic_ns.route('/results')
class ResultList(Resource):
    @jwt_required()
    def get(self):
        results = Result.query.all()
        return [obj_to_dict(r, ['id', 'student_id', 'exam_id', 'marks', 'grade', 'gpa_points']) for r in results]

    @jwt_required()
    @role_required('lecturer', 'registrar', 'super_admin')
    @academic_ns.expect(result_model)
    def post(self):
        data = request.json
        from ...services.grading import calculate_grade_and_gpa
        exam = Exam.query.get(data['exam_id'])
        max_marks = exam.max_marks if exam else 100
        grade, gpa = calculate_grade_and_gpa(data['marks'], float(max_marks))
        result = Result(
            student_id=data['student_id'],
            exam_id=data['exam_id'],
            marks=data['marks'],
            grade=grade,
            gpa_points=gpa
        )
        db.session.add(result)
        db.session.commit()
        return obj_to_dict(result, ['id', 'student_id', 'exam_id', 'marks', 'grade', 'gpa_points']), 201

# ---------- Enrollments ----------
@academic_ns.route('/enrollments/student/<int:user_id>')
class StudentEnrollment(Resource):
    @jwt_required()
    def get(self, user_id):
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return {'message': 'Student not found'}, 404
        enrollments = Enrollment.query.filter_by(student_id=student.id).all()
        result = []
        for enr in enrollments:
            unit = Unit.query.get(enr.unit_id)
            timetable = Timetable.query.filter_by(unit_id=unit.id).all()
            result.append({
                'unit_name': unit.name,
                'timetable_entries': [{
                    'unit_name': unit.name,
                    'day_of_week': tt.day_of_week,
                    'start_time': str(tt.start_time),
                    'end_time': str(tt.end_time),
                    'room': tt.room
                } for tt in timetable]
            })
        return result, 200
