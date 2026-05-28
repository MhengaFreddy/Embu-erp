from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ...models.inventory import Asset, Supplier, PurchaseRequest

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/assets', methods=['GET'])
@jwt_required()
def get_assets():
    assets = Asset.query.all()
    return jsonify([{'id': a.id, 'name': a.name, 'category': a.category, 'serial_number': a.serial_number, 'location': a.location, 'status': a.status} for a in assets])

@inventory_bp.route('/suppliers', methods=['GET'])
@jwt_required()
def get_suppliers():
    suppliers = Supplier.query.all()
    return jsonify([{'id': s.id, 'name': s.name, 'contact_person': s.contact_person, 'phone': s.phone, 'email': s.email} for s in suppliers])

@inventory_bp.route('/purchase-requests', methods=['GET'])
@jwt_required()
def get_purchase_requests():
    prs = PurchaseRequest.query.all()
    return jsonify([{'id': p.id, 'requested_by': p.requested_by, 'item_description': p.item_description, 'status': p.status, 'created_at': str(p.created_at)} for p in prs])
