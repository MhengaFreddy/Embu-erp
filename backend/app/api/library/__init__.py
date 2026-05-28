from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ...models.library import Book, Loan

library_bp = Blueprint('library', __name__)

@library_bp.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    books = Book.query.all()
    return jsonify([{'id': b.id, 'isbn': b.isbn, 'title': b.title, 'author': b.author, 'barcode': b.barcode, 'total_copies': b.total_copies, 'available_copies': b.available_copies} for b in books])

@library_bp.route('/loans', methods=['GET'])
@jwt_required()
def get_loans():
    loans = Loan.query.all()
    return jsonify([{'id': l.id, 'book_id': l.book_id, 'user_id': l.user_id, 'borrow_date': str(l.borrow_date), 'due_date': str(l.due_date), 'return_date': str(l.return_date) if l.return_date else None, 'fine': float(l.fine)} for l in loans])
