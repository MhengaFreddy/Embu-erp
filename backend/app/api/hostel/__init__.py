from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.hostel import Hostel, Room, Allocation
from ...extensions import db
from datetime import date

hostel_ns = Namespace('hostel', description='Hostel management')

room_model = hostel_ns.model('Room', {
    'hostel_id': fields.Integer(required=True),
    'room_number': fields.String(required=True),
    'capacity': fields.Integer(required=True),
    'occupied_beds': fields.Integer(default=0),
    'fee_per_semester': fields.Float(required=True)
})

allocation_model = hostel_ns.model('Allocation', {
    'student_id': fields.Integer(required=True),
    'room_id': fields.Integer(required=True)
})

def obj_to_dict(obj, cols):
    return {col: str(getattr(obj, col)) if isinstance(getattr(obj, col), date) else getattr(obj, col) for col in cols}

# Rooms
@hostel_ns.route('/rooms')
class RoomList(Resource):
    @jwt_required()
    def get(self):
        rooms = Room.query.all()
        cols = ['id', 'hostel_id', 'room_number', 'capacity', 'occupied_beds', 'fee_per_semester']
        return [obj_to_dict(r, cols) for r in rooms]

    @jwt_required()
    @role_required('hostel_manager', 'super_admin')
    @hostel_ns.expect(room_model)
    def post(self):
        data = request.json
        room = Room(**data)
        db.session.add(room)
        db.session.commit()
        return obj_to_dict(room, cols), 201

# Allocations
@hostel_ns.route('/allocations')
class AllocationList(Resource):
    @jwt_required()
    def get(self):
        allocs = Allocation.query.all()
        cols = ['id', 'student_id', 'room_id', 'start_date', 'end_date']
        return [obj_to_dict(a, cols) for a in allocs]

    @jwt_required()
    @role_required('hostel_manager', 'super_admin')
    @hostel_ns.expect(allocation_model)
    def post(self):
        data = request.json
        room = Room.query.get(data['room_id'])
        if not room or room.occupied_beds >= room.capacity:
            return {'message': 'Room full'}, 400
        alloc = Allocation(
            student_id=data['student_id'],
            room_id=data['room_id'],
            start_date=date.today()
        )
        room.occupied_beds += 1
        db.session.add(alloc)
        db.session.commit()
        return obj_to_dict(alloc, cols), 201

@hostel_ns.route('/allocations/<int:id>/vacate')
class VacateRoom(Resource):
    @jwt_required()
    @role_required('hostel_manager', 'super_admin')
    def post(self, id):
        alloc = Allocation.query.get_or_404(id)
        if alloc.end_date:
            return {'message': 'Already vacated'}, 400
        alloc.end_date = date.today()
        room = Room.query.get(alloc.room_id)
        room.occupied_beds -= 1
        db.session.commit()
        return {'message': 'Room vacated'}, 200