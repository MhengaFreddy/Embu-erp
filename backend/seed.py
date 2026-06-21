from app import create_app
from app.extensions import db
from app.models.users import Role, User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    roles = ['super_admin', 'principal', 'registrar', 'finance_officer', 'lecturer', 'student', 'librarian', 'hostel_manager', 'hr_manager']
    for r in roles:
        if not Role.query.filter_by(name=r).first():
            db.session.add(Role(name=r))
    db.session.commit()

    admin_role = Role.query.filter_by(name='super_admin').first()
    if not User.query.filter_by(email='admin@college.edu').first():
        admin = User(
            email='admin@college.edu',
            password_hash=generate_password_hash('admin123'),
            role_id=admin_role.id
        )
        db.session.add(admin)
    # other users
    users = [
        ('hr@college.edu', 'password123', 'hr_manager'),
        ('librarian@college.edu', 'password123', 'librarian'),
        ('finance@college.edu', 'password123', 'finance_officer'),
        ('registrar@college.edu', 'password123', 'registrar'),
        ('hostel@college.edu', 'password123', 'hostel_manager'),
        ('lecturer@college.edu', 'password123', 'lecturer'),
        ('principal@college.edu', 'password123', 'principal'),
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
    print("Database seeded successfully!")
