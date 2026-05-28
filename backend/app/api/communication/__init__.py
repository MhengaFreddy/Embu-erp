from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ...models.communication import Notification
from ...extensions import db
from datetime import datetime

comm_bp = Blueprint('communication', __name__)

@comm_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    data = request.get_json()
    notif = Notification(user_id=data.get('recipient'), message=data.get('message'), channel=data.get('channel', 'email'), sent_at=datetime.utcnow(), status='sent')
    db.session.add(notif)
    db.session.commit()
    return jsonify({'message': 'Notification sent'}), 201

@comm_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    notifs = Notification.query.order_by(Notification.sent_at.desc()).limit(100).all()
    return jsonify([{'id': n.id, 'user_id': n.user_id, 'message': n.message, 'channel': n.channel, 'sent_at': str(n.sent_at), 'status': n.status} for n in notifs])
