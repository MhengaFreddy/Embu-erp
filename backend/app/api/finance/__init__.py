from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.finance import Invoice, Payment, Expense, FeeStructure
from ...extensions import db
from flask import request

finance_ns = Namespace('finance', description='Financial operations')

invoice_model = finance_ns.model('Invoice', {
    'student_id': fields.Integer(required=True),
    'semester_id': fields.Integer(required=True),
    'amount': fields.Float(required=True),
    'due_date': fields.Date(required=True)
})

payment_model = finance_ns.model('Payment', {
    'invoice_id': fields.Integer(required=True),
    'amount': fields.Float(required=True),
    'method': fields.String(required=True),
    'transaction_reference': fields.String
})

@finance_ns.route('/invoices')
class InvoiceList(Resource):
    @jwt_required()
    @role_required('finance_officer', 'super_admin', 'registrar')
    def get(self):
        invoices = Invoice.query.all()
        return [{'id': inv.id, 'student_id': inv.student_id, 'amount': float(inv.amount), 'status': inv.status} for inv in invoices]

    @jwt_required()
    @role_required('finance_officer', 'super_admin')
    @finance_ns.expect(invoice_model)
    def post(self):
        data = request.json
        invoice = Invoice(**data)
        db.session.add(invoice)
        db.session.commit()
        return {'message': 'Invoice created', 'id': invoice.id}, 201

@finance_ns.route('/payments')
class PaymentResource(Resource):
    @jwt_required()
    @role_required('finance_officer', 'super_admin')
    @finance_ns.expect(payment_model)
    def post(self):
        data = request.json
        payment = Payment(**data)
        db.session.add(payment)
        # Update invoice status if fully paid
        invoice = Invoice.query.get(data['invoice_id'])
        total_paid = sum(p.amount for p in invoice.payments) + payment.amount
        if total_paid >= invoice.amount:
            invoice.status = 'paid'
        else:
            invoice.status = 'partial'
        db.session.commit()
        return {'message': 'Payment recorded', 'receipt': payment.receipt_number}, 201

@finance_ns.route('/mpesa/initiate')
class MpesaInitiate(Resource):
    @jwt_required()
    def post(self):
        data = request.json
        from ...services.mpesa import stk_push
        response = stk_push(data['phone'], data['amount'], data['account_reference'])
        return response, 200