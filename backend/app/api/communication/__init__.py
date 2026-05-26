from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.communication import Notification
from ...extensions import db
from datetime import datetime

comm_ns = Namespace('communication', description='Communication & Notifications')

notification_model = comm_ns.model('Notification', {
    'recipient': fields.String(required=True),  # user_id or email
    'channel': fields.String(required=True, enum=['email', 'sms']),
    'message': fields.String(required=True)
})

def obj_to_dict(obj, cols):
    return {col: str(getattr(obj, col)) if isinstance(getattr(obj, col), datetime) else getattr(obj, col) for col in cols}

@comm_ns.route('/send')
class SendMessage(Resource):
    @jwt_required()
    @role_required('super_admin', 'registrar', 'principal')
    @comm_ns.expect(notification_model)
    def post(self):
        data = request.json
        # In production: send actual email/SMS via Celery
        # For now, just store notification
        try:
            user_id = int(data['recipient'])
        except ValueError:
            # Lookup user by email
            from ...models.users import User
            user = User.query.filter_by(email=data['recipient']).first()
            if not user:
                return {'message': 'Recipient not found'}, 404
            user_id = user.id
        notif = Notification(
            user_id=user_id,
            message=data['message'],
            channel=data['channel'],
            sent_at=datetime.utcnow(),
            status='sent'
        )
        db.session.add(notif)
        db.session.commit()
        return {'message': 'Notification queued'}, 201

@comm_ns.route('/notifications')
class NotificationHistory(Resource):
    @jwt_required()
    def get(self):
        notifs = Notification.query.order_by(Notification.sent_at.desc()).limit(100).all()
        cols = ['id', 'user_id', 'message', 'channel', 'sent_at', 'status']
        return [obj_to_dict(n, cols) for n in notifs]