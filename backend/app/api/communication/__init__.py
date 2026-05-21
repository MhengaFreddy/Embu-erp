from flask import Blueprint, request
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.communication import Notification
from ...extensions import db
from datetime import datetime

comm_bp = Blueprint('communication', __name__)
api = Api(comm_bp, doc='/docs')
comm_ns = Namespace('communication', description='Communication & Notifications')
api.add_namespace(comm_ns, path='/')

@comm_ns.route('/send')
class SendMessage(Resource):
    @jwt_required()
    @role_required('super_admin', 'registrar', 'principal')
    def post(self):
        data = request.json
        try:
            user_id = int(data['recipient'])
        except ValueError:
            from ...models.users import User
            user = User.query.filter_by(email=data['recipient']).first()
            if not user:
                return {'message': 'Recipient not found'}, 404
            user_id = user.id
        notif = Notification(user_id=user_id, message=data['message'], channel=data['channel'], sent_at=datetime.utcnow(), status='sent')
        db.session.add(notif)
        db.session.commit()
        return {'message': 'Notification sent'}, 201

@comm_ns.route('/notifications')
class NotificationHistory(Resource):
    @jwt_required()
    def get(self):
        notifs = Notification.query.order_by(Notification.sent_at.desc()).limit(100).all()
        return [{'id': n.id, 'user_id': n.user_id, 'message': n.message, 'channel': n.channel, 'sent_at': str(n.sent_at), 'status': n.status} for n in notifs]
