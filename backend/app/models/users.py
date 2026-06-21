from ..extensions import db
from datetime import datetime

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

    users = db.relationship('User', backref='role', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student_profile = db.relationship('Student', backref='user', uselist=False, lazy=True)
    staff_profile = db.relationship('Staff', backref='user', uselist=False, lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role.name if self.role else None,
            'is_active': self.is_active
        }
