from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

# Customize login message
login_manager.login_view = 'auth.citizen_login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'
