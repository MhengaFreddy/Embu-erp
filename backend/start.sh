#!/bin/bash
set -e

# Create all tables directly (no migration needed)
python -c "
from app import create_app
from app.extensions import db
app = create_app()
with app.app_context():
    db.create_all()
    print('All tables created.')
"

# Seed roles and admin user
python seed.py

# Start the Flask application
exec python run.py