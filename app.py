import os
from flask import Flask
from config import config_by_name
from extensions import db, migrate, login_manager, csrf
from routes import main_bp, auth_bp, citizen_bp, admin_bp
import models


def create_app(config_class=None):
    app = Flask(__name__)

    # Use provided config class (e.g., tests), or select by FLASK_ENV
    if config_class:
        app.config.from_object(config_class)
    else:
        env_name = os.environ.get('FLASK_ENV', 'development')
        app.config.from_object(config_by_name.get(env_name, config_by_name['default']))

    # Ensure upload directory exists (no-op on Render ephemeral FS)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Auto-migration check: add municipality contact columns if missing
    with app.app_context():
        try:
            import sqlalchemy as sa
            inspector = sa.inspect(db.engine)
            if inspector.has_table('municipalities'):
                columns = [c['name'] for c in inspector.get_columns('municipalities')]
                if 'contact_number' not in columns:
                    with db.engine.begin() as conn:
                        conn.execute(db.text("ALTER TABLE municipalities ADD COLUMN contact_number VARCHAR(50)"))
                        conn.execute(db.text("ALTER TABLE municipalities ADD COLUMN contact_email VARCHAR(120)"))
                        conn.execute(db.text("ALTER TABLE municipalities ADD COLUMN office_address TEXT"))
                        conn.execute(db.text("ALTER TABLE municipalities ADD COLUMN office_hours VARCHAR(150)"))
                    print("Auto-migration succeeded: Added contact columns to municipalities table.")
        except Exception as e:
            print(f"Auto-migration warning: {e}")

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(citizen_bp)
    app.register_blueprint(admin_bp)

    # Custom Jinja2 filter: convert UTC → IST (Asia/Kolkata, +05:30)
    @app.template_filter('format_dt')
    def format_dt(dt):
        if not dt:
            return ""
        import datetime
        ist_dt = dt + datetime.timedelta(hours=5, minutes=30)
        return ist_dt.strftime('%d %b %Y, %I:%M %p')

    return app


# ---------------------------------------------------------------------------
# Module-level app instance
# This allows both:
#   gunicorn app:app          (Render auto-detection)
#   gunicorn wsgi:app         (render.yaml explicit command)
# ---------------------------------------------------------------------------
app = create_app()


if __name__ == '__main__':
    # Development server — do NOT use in production
    app.run(host='127.0.0.1', port=5000, debug=True)
