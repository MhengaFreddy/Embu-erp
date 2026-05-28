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
