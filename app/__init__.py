from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(conf_path='config.Config'):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(conf_path)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes import auth_bp, tickets_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)

    return app