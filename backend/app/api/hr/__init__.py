from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.staff import Staff
from ...models.finance import LeaveRequest, Salary
from ...extensions import db

hr_bp = Blueprint('hr', __name__)

# ── List all staff ──
@hr_bp.route('/staff', methods=['GET'])
@jwt_required()
@role_required('hr_manager', 'super_admin', 'principal', 'registrar')
def get_staff():
    staff_list = Staff.query.all()
    return jsonify([{
        'id': s.id,
        'employee_number': s.employee_number,
        'first_name': s.first_name,
        'last_name': s.last_name,
        'designation': s.designation,
        'phone': s.phone
    } for s in staff_list])

# ── Get single staff ──
@hr_bp.route('/staff/<int:id>', methods=['GET'])
@jwt_required()
@role_required('hr_manager', 'super_admin', 'principal', 'registrar')
def get_staff_member(id):
    s = Staff.query.get_or_404(id)
    return jsonify({
        'id': s.id,
        'employee_number': s.employee_number,
        'first_name': s.first_name,
        'last_name': s.last_name,
        'designation': s.designation,
        'phone': s.phone
    })

# ── Create staff ──
@hr_bp.route('/staff', methods=['POST'])
@jwt_required()
@role_required('hr_manager', 'super_admin')
def create_staff():
    data = request.get_json()
    staff = Staff(
        employee_number=data['employee_number'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        designation=data.get('designation'),
        phone=data.get('phone')
    )
    db.session.add(staff)
    db.session.commit()
    return jsonify({'message': 'Staff created', 'id': staff.id}), 201

# ── Update staff ──
@hr_bp.route('/staff/<int:id>', methods=['PUT'])
@jwt_required()
@role_required('hr_manager', 'super_admin')
def update_staff(id):
    s = Staff.query.get_or_404(id)
    data = request.get_json()
    for field in ['employee_number', 'first_name', 'last_name', 'designation', 'phone']:
        if field in data:
            setattr(s, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Staff updated'})

# ── Delete staff ──
@hr_bp.route('/staff/<int:id>', methods=['DELETE'])
@jwt_required()
@role_required('hr_manager', 'super_admin')
def delete_staff(id):
    s = Staff.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    return jsonify({'message': 'Staff deleted'})

# ── Leave requests ──
@hr_bp.route('/leave-requests', methods=['GET'])
@jwt_required()
@role_required('hr_manager', 'super_admin', 'lecturer', 'principal')
def get_leave_requests():
    leaves = LeaveRequest.query.all()
    return jsonify([{
        'id': l.id,
        'staff_id': l.staff_id,
        'start_date': str(l.start_date),
        'end_date': str(l.end_date),
        'leave_type': l.leave_type,
        'status': l.status
    } for l in leaves])

# ── Payroll ──
@hr_bp.route('/payroll', methods=['GET'])
@jwt_required()
@role_required('hr_manager', 'super_admin', 'principal')
def get_payroll():
    salaries = Salary.query.all()
    return jsonify([{
        'id': s.id,
        'staff_id': s.staff_id,
        'month': s.month,
        'basic_pay': float(s.basic_pay),
        'deductions': float(s.deductions),
        'net_pay': float(s.net_pay)
    } for s in salaries])