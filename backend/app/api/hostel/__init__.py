from flask import Blueprint, request
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.hostel import Hostel, Room, Allocation
from ...extensions import db
from datetime import date

hostel_bp = Blueprint('hostel', __name__)
api = Api(hostel_bp, doc='/docs')
hostel_ns = Namespace('hostel', description='Hostel management')
api.add_namespace(hostel_ns, path='/')

@hostel_ns.route('/rooms')
class RoomList(Resource):
    @jwt_required()
    def get(self):
        rooms = Room.query.all()
        return [{'id': r.id, 'hostel_id': r.hostel_id, 'room_number': r.room_number, 'capacity': r.capacity, 'occupied_beds': r.occupied_beds, 'fee_per_semester': float(r.fee_per_semester)} for r in rooms]

@hostel_ns.route('/allocations')
class AllocationList(Resource):
    @jwt_required()
    def get(self):
        allocs = Allocation.query.all()
        return [{'id': a.id, 'student_id': a.student_id, 'room_id': a.room_id, 'start_date': str(a.start_date), 'end_date': str(a.end_date) if a.end_date else None} for a in allocs]

    @jwt_required()
    @role_required('hostel_manager', 'super_admin')
    def post(self):
        data = request.json
        room = Room.query.get(data['room_id'])
        if room.occupied_beds >= room.capacity:
            return {'message': 'Room full'}, 400
        alloc = Allocation(student_id=data['student_id'], room_id=data['room_id'], start_date=date.today())
        room.occupied_beds += 1
        db.session.add(alloc)
        db.session.commit()
        return {'message': 'Room allocated'}, 201
