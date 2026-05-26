from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.inventory import Asset, Supplier, PurchaseRequest
from ...extensions import db
from datetime import datetime

inventory_ns = Namespace('inventory', description='Inventory & Procurement')

asset_model = inventory_ns.model('Asset', {
    'name': fields.String(required=True),
    'category': fields.String(required=True),
    'serial_number': fields.String(required=True),
    'location': fields.String(required=True),
    'status': fields.String(default='active')
})
supplier_model = inventory_ns.model('Supplier', {
    'name': fields.String(required=True),
    'contact_person': fields.String,
    'phone': fields.String,
    'email': fields.String
})
purchase_model = inventory_ns.model('PurchaseRequest', {
    'requested_by': fields.Integer(required=True),
    'item_description': fields.String(required=True)
})

def obj_to_dict(obj, cols):
    return {col: str(getattr(obj, col)) if isinstance(getattr(obj, col), datetime) else getattr(obj, col) for col in cols}

# Assets
@inventory_ns.route('/assets')
class AssetList(Resource):
    @jwt_required()
    def get(self):
        assets = Asset.query.all()
        cols = ['id', 'name', 'category', 'serial_number', 'location', 'status']
        return [obj_to_dict(a, cols) for a in assets]

    @jwt_required()
    @role_required('super_admin')
    @inventory_ns.expect(asset_model)
    def post(self):
        data = request.json
        asset = Asset(**data)
        db.session.add(asset)
        db.session.commit()
        return obj_to_dict(asset, cols), 201

# Suppliers
@inventory_ns.route('/suppliers')
class SupplierList(Resource):
    @jwt_required()
    def get(self):
        suppliers = Supplier.query.all()
        cols = ['id', 'name', 'contact_person', 'phone', 'email']
        return [obj_to_dict(s, cols) for s in suppliers]

    @jwt_required()
    @role_required('super_admin')
    @inventory_ns.expect(supplier_model)
    def post(self):
        data = request.json
        supplier = Supplier(**data)
        db.session.add(supplier)
        db.session.commit()
        return obj_to_dict(supplier, cols), 201

# Purchase Requests
@inventory_ns.route('/purchase-requests')
class PurchaseRequestList(Resource):
    @jwt_required()
    def get(self):
        prs = PurchaseRequest.query.all()
        cols = ['id', 'requested_by', 'item_description', 'status', 'created_at']
        return [obj_to_dict(pr, cols) for pr in prs]

    @jwt_required()
    @role_required('super_admin')
    @inventory_ns.expect(purchase_model)
    def post(self):
        data = request.json
        pr = PurchaseRequest(
            requested_by=data['requested_by'],
            item_description=data['item_description'],
            status='pending',
            created_at=datetime.utcnow()
        )
        db.session.add(pr)
        db.session.commit()
        return obj_to_dict(pr, cols), 201