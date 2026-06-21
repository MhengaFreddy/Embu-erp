from flask import Blueprint, request
from flask_restx import Api, Namespace, Resource
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.finance import Invoice, Payment, Expense
from ...extensions import db

finance_bp = Blueprint('finance', __name__)
api = Api(finance_bp, doc='/docs')
finance_ns = Namespace('finance', description='Financial operations')
api.add_namespace(finance_ns, path='/')

@finance_ns.route('/invoices')
class InvoiceList(Resource):
    @jwt_required()
    @role_required('finance_officer', 'super_admin', 'registrar', 'principal')
    def get(self):
        invoices = Invoice.query.all()
        return [{'id': inv.id, 'student_id': inv.student_id, 'amount': float(inv.amount), 'status': inv.status} for inv in invoices]

@finance_ns.route('/payments')
class PaymentResource(Resource):
    @jwt_required()
    @role_required('finance_officer', 'super_admin', 'registrar', 'principal')
    def get(self):
        payments = Payment.query.all()
        return [{'id': p.id, 'invoice_id': p.invoice_id, 'amount': float(p.amount), 'method': p.method, 'payment_date': str(p.payment_date)} for p in payments]

@finance_ns.route('/expenses')
class ExpenseList(Resource):
    @jwt_required()
    @role_required('finance_officer', 'super_admin', 'registrar', 'principal')
    def get(self):
        expenses = Expense.query.all()
        return [{'id': e.id, 'description': e.description, 'amount': float(e.amount), 'category': e.category, 'date': str(e.date)} for e in expenses]
