#!/bin/bash
set -e

# ──────────────────────────────────────
# Self‑repair: force the correct auth blueprint
# (just in case the deployed file is outdated)
# ──────────────────────────────────────
cat > /app/app/api/auth/__init__.py << 'AUTH_EOF'
from flask import Blueprint, request, jsonify
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from ...models.users import User, Role
from ...extensions import db

auth_bp = Blueprint('auth', __name__)
api = Api(auth_bp, doc='/docs')

auth_ns = Namespace('auth', description='Authentication operations')
api.add_namespace(auth_ns, path='/')

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

register_model = auth_ns.model('Register', {
    'email': fields.String(required=True),
    'password': fields.String(required=True),
    'role': fields.String(required=True)
})

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        data = request.json
        user = User.query.filter_by(email=data['email']).first()
        if not user or not check_password_hash(user.password_hash, data['password']):
            return {'message': 'Invalid credentials'}, 401

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }, 200

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    def post(self):
        data = request.json
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already registered'}, 400

        role = Role.query.filter_by(name=data['role']).first()
        if not role:
            return {'message': 'Invalid role'}, 400

        hashed_pw = generate_password_hash(data['password'])
        new_user = User(email=data['email'], password_hash=hashed_pw, role_id=role.id)
        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User registered successfully'}, 201

@auth_ns.route('/refresh')
class RefreshToken(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        return {'access_token': new_access_token}, 200
AUTH_EOF

# ──────────────────────────────────────
# Normal startup
# ──────────────────────────────────────
export FLASK_APP=run.py
python seed.py
exec python run.py