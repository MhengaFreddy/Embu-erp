from app import create_app
from app.extensions import db
from app.models.users import Role, User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Roles
    roles = ['super_admin', 'principal', 'registrar', 'finance_officer',
             'lecturer', 'student', 'librarian', 'hostel_manager', 'hr_manager']
    for r in roles:
        if not Role.query.filter_by(name=r).first():
            db.session.add(Role(name=r))
    db.session.commit()

    # Admin user
    admin_role = Role.query.filter_by(name='super_admin').first()
    if not User.query.filter_by(email='admin@embucollege.ac.ke').first():
        admin = User(
            email='admin@embucollege.ac.ke',
            password_hash=generate_password_hash('admin123'),
            role_id=admin_role.id
        )
        db.session.add(admin)

    # All other users
    users = [
        ('hr.manager@embucollege.ac.ke', 'password123', 'hr_manager'),
        ('librarian@embucollege.ac.ke', 'password123', 'librarian'),
        ('finance@embucollege.ac.ke', 'password123', 'finance_officer'),
        ('registrar@embucollege.ac.ke', 'password123', 'registrar'),
        ('hostel@embucollege.ac.ke', 'password123', 'hostel_manager'),
        ('lecturer@embucollege.ac.ke', 'password123', 'lecturer'),
        ('principal@embucollege.ac.ke', 'password123', 'principal'),
        ('superadmin2@embucollege.ac.ke', 'password123', 'super_admin')
    ]
    for email, pw, role_name in users:
        if not User.query.filter_by(email=email).first():
            role = Role.query.filter_by(name=role_name).first()
            user = User(
                email=email,
                password_hash=generate_password_hash(pw),
                role_id=role.id
            )
            db.session.add(user)

    db.session.commit()
    print("All users seeded successfully!")