from flask import Flask, send_from_directory, abort
from flask_cors import CORS
from .config import Config
from .extensions import db, migrate, jwt, ma
import os

def create_app(config_class=Config):
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    CORS(app)

    # ---------- API Blueprints FIRST (so they take precedence) ----------
    from .api.auth import auth_bp
    from .api.students import students_bp
    from .api.finance import finance_bp
    from .api.academic import academic_bp
    from .api.hr import hr_bp
    from .api.library import library_bp
    from .api.hostel import hostel_bp
    from .api.inventory import inventory_bp
    from .api.communication import comm_bp
    from .api.dashboard import dashboard_bp
    from .api.lecturer import lecturer_bp
    from .api.users import users_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(finance_bp, url_prefix='/api/finance')
    app.register_blueprint(academic_bp, url_prefix='/api/academic')
    app.register_blueprint(hr_bp, url_prefix='/api/hr')
    app.register_blueprint(library_bp, url_prefix='/api/library')
    app.register_blueprint(hostel_bp, url_prefix='/api/hostel')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(comm_bp, url_prefix='/api/communication')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(lecturer_bp, url_prefix='/api/lecturer')
    app.register_blueprint(users_bp, url_prefix='/api/users')

    # ---------- Static file serving (works locally AND on Railway) ----------
    current_dir = os.path.dirname(os.path.abspath(__file__))  # backend/app
    backend_dir = os.path.dirname(current_dir)                 # backend
    
    # Local: frontend is at ../frontend (relative to backend folder)
    local_frontend = os.path.join(backend_dir, '..', 'frontend')
    # Railway: frontend is copied inside backend/
    railway_frontend = os.path.join(backend_dir, 'frontend')
    
    if os.path.isdir(local_frontend):
        frontend_path = os.path.realpath(local_frontend)
    elif os.path.isdir(railway_frontend):
        frontend_path = railway_frontend
    else:
        frontend_path = railway_frontend  # fallback, may be missing
        print(f"WARNING: frontend folder not found at {local_frontend} or {railway_frontend}")

    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        return send_from_directory(os.path.join(frontend_path, 'assets'), filename)

    @app.route('/')
    def root():
        return send_from_directory(frontend_path, 'index.html')

    # This catch-all will only match paths that are NOT already handled by blueprints
    @app.route('/<path:page>')
    def serve_page(page):
        if page.startswith('api/'):
            abort(404)
        return send_from_directory(frontend_path, page)

    # ---------- JWT user loader ----------
    from .models.users import User

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = int(jwt_data["sub"])
        return User.query.filter_by(id=identity).one_or_none()

    return app