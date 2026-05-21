from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ...models.users import User
from ...utils.decorators import role_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('super_admin', 'principal')
def get_users():
    users = User.query.all()
    result = []
    for u in users:
        result.append({
            'id': u.id,
            'email': u.email,
            'role': u.role.name if u.role else 'N/A',
            'is_active': u.is_active,
            'last_login': str(u.last_login) if u.last_login else None,
            'created_at': str(u.created_at)
        })
    return jsonify(result)