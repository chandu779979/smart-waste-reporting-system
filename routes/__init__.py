from routes.main import main_bp
from routes.auth import auth_bp
from routes.citizen import citizen_bp
from routes.admin import admin_bp

__all__ = [
    'main_bp',
    'auth_bp',
    'citizen_bp',
    'admin_bp'
]
