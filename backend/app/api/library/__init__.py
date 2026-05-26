from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.library import Book, Loan
from ...extensions import db
from datetime import date, timedelta

library_ns = Namespace('library', description='Library management')

book_model = library_ns.model('Book', {
    'isbn': fields.String(required=True),
    'title': fields.String(required=True),
    'author': fields.String(required=True),
    'barcode': fields.String(required=True),
    'total_copies': fields.Integer(required=True),
    'available_copies': fields.Integer(required=True)
})

loan_model = library_ns.model('Loan', {
    'book_id': fields.Integer(required=True),
    'user_id': fields.Integer(required=True)
})

def obj_to_dict(obj, cols):
    return {col: str(getattr(obj, col)) if isinstance(getattr(obj, col), date) else getattr(obj, col) for col in cols}

# Books
@library_ns.route('/books')
class BookList(Resource):
    @jwt_required()
    def get(self):
        books = Book.query.all()
        cols = ['id', 'isbn', 'title', 'author', 'barcode', 'total_copies', 'available_copies']
        return [obj_to_dict(b, cols) for b in books]

    @jwt_required()
    @role_required('librarian', 'super_admin')
    @library_ns.expect(book_model)
    def post(self):
        data = request.json
        book = Book(**data)
        db.session.add(book)
        db.session.commit()
        return obj_to_dict(book, cols), 201

@library_ns.route('/books/<int:id>')
class BookDetail(Resource):
    @jwt_required()
    @role_required('librarian', 'super_admin')
    def put(self, id):
        book = Book.query.get_or_404(id)
        data = request.json
        for key in ['isbn', 'title', 'author', 'barcode', 'total_copies', 'available_copies']:
            if key in data:
                setattr(book, key, data[key])
        db.session.commit()
        return obj_to_dict(book, cols)

    @jwt_required()
    @role_required('super_admin')
    def delete(self, id):
        book = Book.query.get_or_404(id)
        db.session.delete(book)
        db.session.commit()
        return {'message': 'Book deleted'}, 200

# Loans
@library_ns.route('/loans')
class LoanList(Resource):
    @jwt_required()
    def get(self):
        loans = Loan.query.all()
        cols = ['id', 'book_id', 'user_id', 'borrow_date', 'due_date', 'return_date', 'fine']
        return [obj_to_dict(l, cols) for l in loans]

    @jwt_required()
    @role_required('librarian', 'super_admin')
    @library_ns.expect(loan_model)
    def post(self):
        data = request.json
        book = Book.query.get(data['book_id'])
        if not book or book.available_copies < 1:
            return {'message': 'Book not available'}, 400
        # Create loan
        loan = Loan(
            book_id=data['book_id'],
            user_id=data['user_id'],
            borrow_date=date.today(),
            due_date=date.today() + timedelta(days=14)  # 14 days loan period
        )
        book.available_copies -= 1
        db.session.add(loan)
        db.session.commit()
        return obj_to_dict(loan, cols), 201

@library_ns.route('/loans/<int:id>/return')
class ReturnBook(Resource):
    @jwt_required()
    @role_required('librarian', 'super_admin')
    def post(self, id):
        loan = Loan.query.get_or_404(id)
        if loan.return_date:
            return {'message': 'Book already returned'}, 400
        loan.return_date = date.today()
        # Calculate fine (e.g., KES 10 per day overdue)
        if loan.return_date > loan.due_date:
            overdue_days = (loan.return_date - loan.due_date).days
            loan.fine = overdue_days * 10
        book = Book.query.get(loan.book_id)
        book.available_copies += 1
        db.session.commit()
        return obj_to_dict(loan, ['id', 'book_id', 'return_date', 'fine']), 200