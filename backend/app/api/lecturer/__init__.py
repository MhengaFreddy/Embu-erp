from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.staff import Staff
from ...models.academic import Timetable, Unit

lecturer_bp = Blueprint('lecturer', __name__)

@lecturer_bp.route('/my-units', methods=['GET'])
@jwt_required()
def my_units():
    user_id = int(get_jwt_identity())
    staff = Staff.query.filter_by(user_id=user_id).first()
    if not staff:
        return jsonify([])
    entries = Timetable.query.filter_by(lecturer_id=staff.id).all()
    unit_ids = list(set(e.unit_id for e in entries))
    units = Unit.query.filter(Unit.id.in_(unit_ids)).all()
    result = []
    for u in units:
        result.append({'unit_id': u.id, 'unit_name': u.name, 'unit_code': u.code})
    return jsonify(result)
