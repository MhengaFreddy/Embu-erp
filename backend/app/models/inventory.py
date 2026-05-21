from ..extensions import db
from datetime import datetime

class Asset(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(50))
    serial_number = db.Column(db.String(50), unique=True)
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')

class PurchaseRequest(db.Model):
    __tablename__ = 'purchase_requests'
    id = db.Column(db.Integer, primary_key=True)
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    item_description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100))
