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
        result = []
        for inv in invoices:
            result.append({
                'id': inv.id,
                'student_id': inv.student_id,
                'amount': float(inv.amount),
                'status': inv.status
            })
        return result

    @jwt_required()
    @role_required('finance_officer', 'super_admin')
    def post(self):
        data = request.get_json()
        invoice = Invoice(
            student_id=data['student_id'],
            semester_id=data.get('semester_id'),
            amount=data['amount'],
            due_date=data['due_date']
        )
        db.session.add(invoice)
        db.session.commit()
        return {'message': 'Invoice created', 'id': invoice.id}, 201

@finance_ns.route('/payments')
class PaymentResource(Resource):
    @jwt_required()
    @role_required('finance_officer', 'super_admin', 'registrar', 'principal')
    def get(self):
        payments = Payment.query.all()
        result = []
        for p in payments:
            result.append({
                'id': p.id,
                'invoice_id': p.invoice_id,
                'amount': float(p.amount),
                'method': p.method,
                'payment_date': str(p.payment_date)
            })
        return result

    @jwt_required()
    @role_required('finance_officer', 'super_admin')
    def post(self):
        data = request.get_json()
        payment = Payment(
            invoice_id=data['invoice_id'],
            amount=data['amount'],
            method=data['method'],
            transaction_reference=data.get('transaction_reference')
        )
        db.session.add(payment)
        invoice = Invoice.query.get(data['invoice_id'])
        if invoice:
            total_paid = sum(p.amount for p in invoice.payments) + payment.amount
            invoice.status = 'paid' if total_paid >= invoice.amount else 'partial'
        db.session.commit()
        return {'message': 'Payment recorded'}, 201

@finance_ns.route('/expenses')
class ExpenseList(Resource):
    @jwt_required()
    @role_required('finance_officer', 'super_admin', 'registrar', 'principal')
    def get(self):
        expenses = Expense.query.all()
        result = []
        for e in expenses:
            result.append({
                'id': e.id,
                'description': e.description,
                'amount': float(e.amount),
                'category': e.category,
                'date': str(e.date)
            })
        return result