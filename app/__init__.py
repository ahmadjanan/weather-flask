from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config.settings import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

from app.models.users import User


def init_app():
    """Initialize the core application."""
    with app.app_context():
        # Include our Routes
        from app.routes.api import api_bp
        from app.routes.auth import auth_bp

        # Register Blueprints
        app.register_blueprint(auth_bp)
        app.register_blueprint(api_bp)

        return app
