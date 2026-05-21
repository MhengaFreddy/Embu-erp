from flask import Blueprint, request
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.library import Book, Loan
from ...extensions import db
from datetime import date, timedelta

library_bp = Blueprint('library', __name__)
api = Api(library_bp, doc='/docs')
library_ns = Namespace('library', description='Library management')
api.add_namespace(library_ns, path='/')

@library_ns.route('/books')
class BookList(Resource):
    @jwt_required()
    def get(self):
        books = Book.query.all()
        return [{'id': b.id, 'isbn': b.isbn, 'title': b.title, 'author': b.author, 'barcode': b.barcode, 'total_copies': b.total_copies, 'available_copies': b.available_copies} for b in books]

    @jwt_required()
    @role_required('librarian', 'super_admin')
    def post(self):
        data = request.json
        book = Book(**data)
        db.session.add(book)
        db.session.commit()
        return {'message': 'Book added', 'id': book.id}, 201

@library_ns.route('/loans')
class LoanList(Resource):
    @jwt_required()
    def get(self):
        loans = Loan.query.all()
        return [{'id': l.id, 'book_id': l.book_id, 'user_id': l.user_id, 'borrow_date': str(l.borrow_date), 'due_date': str(l.due_date), 'return_date': str(l.return_date) if l.return_date else None, 'fine': float(l.fine)} for l in loans]

    @jwt_required()
    @role_required('librarian', 'super_admin')
    def post(self):
        data = request.json
        book = Book.query.get(data['book_id'])
        if book.available_copies < 1:
            return {'message': 'Book not available'}, 400
        loan = Loan(book_id=data['book_id'], user_id=data['user_id'], borrow_date=date.today(), due_date=date.today() + timedelta(days=14))
        book.available_copies -= 1
        db.session.add(loan)
        db.session.commit()
        return {'message': 'Book loaned', 'id': loan.id}, 201
