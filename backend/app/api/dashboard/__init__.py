from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ...models.students import Student
from ...models.finance import Payment
from ...models.staff import Staff
from ...models.library import Book
from ...extensions import db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    return jsonify({
        'total_students': Student.query.count(),
        'fee_collected': float(db.session.query(func.coalesce(func.sum(Payment.amount), 0)).scalar()),
        'total_staff': Staff.query.count(),
        'total_books': Book.query.count(),
        'enrollment_labels': ['Jan','Feb','Mar','Apr','May'],
        'enrollment_data': [5,10,15,20,25],
        'revenue_labels': ['Jan','Feb','Mar','Apr','May'],
        'revenue_data': [5000,10000,15000,20000,25000]
    })
