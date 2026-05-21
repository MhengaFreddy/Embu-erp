from flask import Blueprint, request
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ...utils.decorators import role_required
from ...models.inventory import Asset, PurchaseRequest, Supplier
from ...extensions import db

inventory_bp = Blueprint('inventory', __name__)
api = Api(inventory_bp, doc='/docs')
inventory_ns = Namespace('inventory', description='Inventory & Procurement')
api.add_namespace(inventory_ns, path='/')

@inventory_ns.route('/assets')
class AssetList(Resource):
    @jwt_required()
    def get(self):
        assets = Asset.query.all()
        return [{'id': a.id, 'name': a.name, 'category': a.category, 'serial_number': a.serial_number, 'location': a.location, 'status': a.status} for a in assets]

@inventory_ns.route('/suppliers')
class SupplierList(Resource):
    @jwt_required()
    def get(self):
        suppliers = Supplier.query.all()
        return [{'id': s.id, 'name': s.name, 'contact_person': s.contact_person, 'phone': s.phone, 'email': s.email} for s in suppliers]

@inventory_ns.route('/purchase-requests')
class PurchaseRequestList(Resource):
    @jwt_required()
    def get(self):
        prs = PurchaseRequest.query.all()
        return [{'id': p.id, 'requested_by': p.requested_by, 'item_description': p.item_description, 'status': p.status, 'created_at': str(p.created_at)} for p in prs]
