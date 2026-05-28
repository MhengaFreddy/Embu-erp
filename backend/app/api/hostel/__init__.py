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
