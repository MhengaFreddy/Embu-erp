import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://embu:password@localhost:5432/embu_college')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY')
    MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET')
    MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE')
    MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY')
