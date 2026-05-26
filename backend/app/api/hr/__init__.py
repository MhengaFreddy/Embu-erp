from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.staff import Staff
from ...models.finance import LeaveRequest, Salary
from ...extensions import db

hr_ns = Namespace('hr', description='Human Resources')

staff_model = hr_ns.model('Staff', {
    'employee_number': fields.String(required=True),
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'department_id': fields.Integer,
    'designation': fields.String,
    'date_joined': fields.Date,
    'phone': fields.String
})

leave_model = hr_ns.model('LeaveRequest', {
    'staff_id': fields.Integer(required=True),
    'start_date': fields.Date(required=True),
    'end_date': fields.Date(required=True),
    'leave_type': fields.String(required=True)
})

salary_model = hr_ns.model('Salary', {
    'staff_id': fields.Integer(required=True),
    'month': fields.String(required=True),
    'basic_pay': fields.Float(required=True),
    'deductions': fields.Float(required=True),
    'net_pay': fields.Float(required=True)
})

def obj_to_dict(obj, cols):
    return {col: str(getattr(obj, col)) if hasattr(getattr(obj, col), 'isoformat') else getattr(obj, col) for col in cols}

# ---------- Staff ----------
@hr_ns.route('/staff')
class StaffList(Resource):
    @jwt_required()
    @role_required('hr_manager', 'super_admin')
    def get(self):
        staff = Staff.query.all()
        cols = ['id', 'employee_number', 'first_name', 'last_name', 'designation', 'phone']
        return [obj_to_dict(s, cols) for s in staff]

    @jwt_required()
    @role_required('hr_manager', 'super_admin')
    @hr_ns.expect(staff_model)
    def post(self):
        data = request.json
        # Also create User with role 'lecturer' or appropriate
        s = Staff(**data)
        db.session.add(s)
        db.session.commit()
        return obj_to_dict(s, cols), 201

@hr_ns.route('/staff/<int:id>')
class StaffDetail(Resource):
    @jwt_required()
    @role_required('hr_manager', 'super_admin')
    def put(self, id):
        s = Staff.query.get_or_404(id)
        data = request.json
        for key in ['employee_number', 'first_name', 'last_name', 'department_id', 'designation', 'phone']:
            if key in data:
                setattr(s, key, data[key])
        db.session.commit()
        return obj_to_dict(s, ['id', 'employee_number', 'first_name', 'last_name', 'designation'])

    @jwt_required()
    @role_required('super_admin')
    def delete(self, id):
        s = Staff.query.get_or_404(id)
        db.session.delete(s)
        db.session.commit()
        return {'message': 'Staff deleted'}, 200

# ---------- Leave Requests ----------
@hr_ns.route('/leave-requests')
class LeaveList(Resource):
    @jwt_required()
    @role_required('hr_manager', 'super_admin', 'lecturer')
    def get(self):
        leaves = LeaveRequest.query.all()
        cols = ['id', 'staff_id', 'start_date', 'end_date', 'leave_type', 'status']
        return [obj_to_dict(l, cols) for l in leaves]

    @jwt_required()
    @role_required('hr_manager', 'super_admin', 'lecturer')
    @hr_ns.expect(leave_model)
    def post(self):
        data = request.json
        lr = LeaveRequest(**data)
        db.session.add(lr)
        db.session.commit()
        return obj_to_dict(lr, cols), 201

# ---------- Payroll ----------
@hr_ns.route('/payroll')
class PayrollList(Resource):
    @jwt_required()
    @role_required('hr_manager', 'super_admin')
    def get(self):
        salaries = Salary.query.all()
        cols = ['id', 'staff_id', 'month', 'basic_pay', 'deductions', 'net_pay']
        return [obj_to_dict(s, cols) for s in salaries]

    @jwt_required()
    @role_required('hr_manager', 'super_admin')
    @hr_ns.expect(salary_model)
    def post(self):
        data = request.json
        sal = Salary(**data)
        db.session.add(sal)
        db.session.commit()
        return obj_to_dict(sal, cols), 201