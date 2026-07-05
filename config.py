import os
from dotenv import load_dotenv

# Load .env only in development (Render injects env vars directly)
load_dotenv()

def _fix_db_url(url: str) -> str:
    """
    Render's managed PostgreSQL provides a URL starting with 'postgres://'
    but SQLAlchemy 1.4+ requires 'postgresql://'.
    This fix is applied transparently at startup.
    """
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    # -------------------------------------------------------------------------
    # Core Flask settings
    # -------------------------------------------------------------------------
    SECRET_KEY = os.environ.get('SECRET_KEY', '947eefba942e887f481cde3ef2f8190c')
    DEBUG = False
    TESTING = False

    # -------------------------------------------------------------------------
    # Database (PostgreSQL)
    # Render injects DATABASE_URL automatically when a database is linked.
    # -------------------------------------------------------------------------
    SQLALCHEMY_DATABASE_URI = _fix_db_url(
        os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/swm_db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        # Recycle connections every 30 min to prevent stale connection errors
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    }

    # -------------------------------------------------------------------------
    # Google Maps API Key
    # -------------------------------------------------------------------------
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '').strip('\'"')

    # -------------------------------------------------------------------------
    # File uploads
    # Render's filesystem is ephemeral — uploaded images won't persist across
    # deploys. For production, migrate uploads to S3/Cloudinary.
    # The folder is still created at startup so the app doesn't crash.
    # -------------------------------------------------------------------------
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 5242880))  # 5 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# Active config is selected by FLASK_ENV environment variable
config_by_name = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
