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
    day_of_week = db.Column(db.SmallInteger)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    room = db.Column(db.String(20))

class Exam(db.Model):
    __tablename__ = 'exams'
    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'))
    exam_date = db.Column(db.Date)
    exam_type = db.Column(db.String(20))  # 'CAT1','CAT2','FINAL'
    max_marks = db.Column(db.Numeric(5,2))

    results = db.relationship('Result', backref='exam', lazy=True)

class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'))
    marks = db.Column(db.Numeric(5,2))
    grade = db.Column(db.String(2))  # A,B,C,D,F
    gpa_points = db.Column(db.Numeric(3,2))
