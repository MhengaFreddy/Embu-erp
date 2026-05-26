from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.academic import Department, Course, Semester, Unit, Enrollment, Timetable, Exam, Result
from ...extensions import db
from ...schemas.student import student_schema, students_schema  # if needed; we can create specific schemas later

academic_ns = Namespace('academic', description='Academic operations')

# ---------- Models for Swagger (simplified) ----------
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
    'start_time': fields.String(required=True),  # format HH:MM
    'end_time': fields.String(required=True),
    'room': fields.String(required=True)
})
exam_model = academic_ns.model('Exam', {
    'unit_id': fields.Integer(required=True),
    'exam_date': fields.Date(required=True),
    'exam_type': fields.String(required=True),  # CAT1, CAT2, FINAL
    'max_marks': fields.Float(required=True)
})
result_model = academic_ns.model('Result', {
    'student_id': fields.Integer(required=True),
    'exam_id': fields.Integer(required=True),
    'marks': fields.Float(required=True)
})

# ---------- Helper to convert objects to dict ----------
def obj_to_dict(obj, columns):
    return {col: getattr(obj, col) for col in columns}

# ---------- Departments ----------
@academic_ns.route('/departments')
class DepartmentList(Resource):
    @jwt_required()
    def get(self):
        depts = Department.query.all()
        cols = ['id', 'name', 'code']
        return [obj_to_dict(d, cols) for d in depts]

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
        dept.name = data.get('name', dept.name)
        dept.code = data.get('code', dept.code)
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
        cols = ['id', 'name', 'code', 'department_id']
        return [obj_to_dict(c, cols) for c in courses]

    @jwt_required()
    @role_required('registrar', 'super_admin')
    @academic_ns.expect(course_model)
    def post(self):
        data = request.json
        course = Course(name=data['name'], code=data['code'], department_id=data['department_id'])
        db.session.add(course)
        db.session.commit()
        return obj_to_dict(course, cols), 201

@academic_ns.route('/courses/<int:id>')
class CourseDetail(Resource):
    @jwt_required()
    @role_required('registrar', 'super_admin')
    def put(self, id):
        course = Course.query.get_or_404(id)
        data = request.json
        course.name = data.get('name', course.name)
        course.code = data.get('code', course.code)
        course.department_id = data.get('department_id', course.department_id)
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
        cols = ['id', 'name', 'code', 'course_id', 'semester_id', 'credit_hours']
        return [obj_to_dict(u, cols) for u in units]

    @jwt_required()
    @role_required('registrar', 'super_admin')
    @academic_ns.expect(unit_model)
    def post(self):
        data = request.json
        unit = Unit(**data)
        db.session.add(unit)
        db.session.commit()
        return obj_to_dict(unit, cols), 201

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
        return obj_to_dict(unit, cols)

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
        cols = ['id', 'unit_id', 'lecturer_id', 'day_of_week', 'start_time', 'end_time', 'room']
        # Convert times to strings
        result = []
        for e in entries:
            d = obj_to_dict(e, cols)
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
        return obj_to_dict(tt, cols), 201

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
        return obj_to_dict(tt, cols)

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
        cols = ['id', 'unit_id', 'exam_date', 'exam_type', 'max_marks']
        return [obj_to_dict(e, cols) for e in exams]

    @jwt_required()
    @role_required('registrar', 'super_admin')
    @academic_ns.expect(exam_model)
    def post(self):
        data = request.json
        exam = Exam(**data)
        db.session.add(exam)
        db.session.commit()
        return obj_to_dict(exam, cols), 201

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
        return obj_to_dict(exam, cols)

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
        cols = ['id', 'student_id', 'exam_id', 'marks', 'grade', 'gpa_points']
        return [obj_to_dict(r, cols) for r in results]

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
        return obj_to_dict(result, cols), 201

@academic_ns.route('/results/<int:id>')
class ResultDetail(Resource):
    @jwt_required()
    @role_required('lecturer', 'registrar', 'super_admin')
    def put(self, id):
        result = Result.query.get_or_404(id)
        data = request.json
        if 'marks' in data:
            result.marks = data['marks']
            exam = Exam.query.get(result.exam_id)
            max_marks = exam.max_marks if exam else 100
            result.grade, result.gpa_points = calculate_grade_and_gpa(data['marks'], float(max_marks))
        db.session.commit()
        return obj_to_dict(result, cols)

    @jwt_required()
    @role_required('super_admin')
    def delete(self, id):
        result = Result.query.get_or_404(id)
        db.session.delete(result)
        db.session.commit()
        return {'message': 'Result deleted'}, 200

# ---------- Enrollments (for student timetable display) ----------
@academic_ns.route('/enrollments/student/<int:user_id>')
class StudentEnrollment(Resource):
    @jwt_required()
    def get(self, user_id):
        # user_id is actually student's user_id; need student record
        from ...models.students import Student
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