import os
from flask import Flask
from config import Config
from extensions import db, migrate, login_manager, csrf
from routes import main_bp, auth_bp, citizen_bp, admin_bp
import models

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure upload directory exists locally
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Run auto-migration check for new contact fields in municipalities table
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
    
    # Custom template filter for Asia/Kolkata (IST, UTC+05:30)
    @app.template_filter('format_dt')
    def format_dt(dt):
        if not dt:
            return ""
        import datetime
        ist_dt = dt + datetime.timedelta(hours=5, minutes=30)
        return ist_dt.strftime('%d %b %Y, %I:%M %p')
        
    return app

if __name__ == '__main__':
    app = create_app()
    # Runs on local port 5000 by default
    app.run(host='127.0.0.1', port=5000, debug=True)
