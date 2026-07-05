"""
WSGI entry point for production deployment (Gunicorn / Render).
Gunicorn runs:  gunicorn wsgi:app
"""
from app import create_app

app = create_app()
