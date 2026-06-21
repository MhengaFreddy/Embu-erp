from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import abort
from ..models.users import User

def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or user.role.name not in roles:
                abort(403, description="Insufficient permissions")
            return fn(*args, **kwargs)
        return wrapper
    return decorator
