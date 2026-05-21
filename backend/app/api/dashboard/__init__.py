from flask import Blueprint
from flask_restx import Api, Namespace, Resource
from flask_jwt_extended import jwt_required
from ...models.students import Student
from ...models.finance import Payment
from ...models.staff import Staff
from ...models.library import Book
from ...extensions import db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)
api = Api(dashboard_bp, doc='/docs')
dashboard_ns = Namespace('dashboard', description='Dashboard statistics')
api.add_namespace(dashboard_ns, path='/')

@dashboard_ns.route('/stats')
class DashboardStats(Resource):
    @jwt_required()
    def get(self):
        total_students = Student.query.count()
        total_fees = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).scalar()
        total_staff = Staff.query.count()
        total_books = Book.query.count()

        return {
            'total_students': total_students,
            'fee_collected': float(total_fees),
            'total_staff': total_staff,
            'total_books': total_books,
            'enrollment_labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'enrollment_data': [5, 10, 15, 20, 25],
            'revenue_labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'revenue_data': [5000, 10000, 15000, 20000, 25000]
        }, 200