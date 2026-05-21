from flask import Blueprint, request
from flask_restx import Api, Namespace, Resource
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.academic import Department, Course, Unit, Timetable, Exam, Result
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
    @role_required('registrar', 'super_admin', 'principal', 'lecturer')
    def get(self):
        depts = Department.query.all()
        return [obj_to_dict(d, ['id', 'name', 'code']) for d in depts]

@academic_ns.route('/courses')
class CourseList(Resource):
    @jwt_required()
    @role_required('registrar', 'super_admin', 'principal', 'lecturer')
    def get(self):
        courses = Course.query.all()
        return [obj_to_dict(c, ['id', 'name', 'code', 'department_id']) for c in courses]

@academic_ns.route('/units')
class UnitList(Resource):
    @jwt_required()
    @role_required('registrar', 'super_admin', 'principal', 'lecturer')
    def get(self):
        units = Unit.query.all()
        return [obj_to_dict(u, ['id', 'name', 'code', 'course_id', 'semester_id', 'credit_hours']) for u in units]

@academic_ns.route('/timetable')
class TimetableList(Resource):
    @jwt_required()
    @role_required('registrar', 'super_admin', 'principal', 'lecturer')
    def get(self):
        entries = Timetable.query.all()
        return [{'id': e.id, 'unit_id': e.unit_id, 'lecturer_id': e.lecturer_id, 'day_of_week': e.day_of_week, 'start_time': str(e.start_time), 'end_time': str(e.end_time), 'room': e.room} for e in entries]

@academic_ns.route('/exams')
class ExamList(Resource):
    @jwt_required()
    @role_required('registrar', 'super_admin', 'principal', 'lecturer')
    def get(self):
        exams = Exam.query.all()
        return [obj_to_dict(e, ['id', 'unit_id', 'exam_date', 'exam_type', 'max_marks']) for e in exams]

@academic_ns.route('/results')
class ResultList(Resource):
    @jwt_required()
    @role_required('registrar', 'super_admin', 'principal', 'lecturer')
    def get(self):
        results = Result.query.all()
        return [obj_to_dict(r, ['id', 'student_id', 'exam_id', 'marks', 'grade', 'gpa_points']) for r in results]