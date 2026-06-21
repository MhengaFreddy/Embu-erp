from ..extensions import db
from datetime import date

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20))
    title = db.Column(db.String(200))
    author = db.Column(db.String(100))
    barcode = db.Column(db.String(50), unique=True)
    total_copies = db.Column(db.Integer)
    available_copies = db.Column(db.Integer)

class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    borrow_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    return_date = db.Column(db.Date, nullable=True)
    fine = db.Column(db.Numeric(10,2), default=0)
