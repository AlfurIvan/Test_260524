import os

from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint

from .config import Config

db = SQLAlchemy()
api = Api()
bcrypt = Bcrypt()
migrate = Migrate()


def create_app(conf=Config):
    app = Flask(__name__)
    app.config.from_object(conf)

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    from .resources import initialize_resources
    api = Api(app)
    initialize_resources(api)

    swagger_init(app)

    return app


def swagger_init(app):
    @app.route("/spec")
    def spec():
        swag = swagger(app)
        swag['info']['version'] = "1.0"
        swag['info']['title'] = "My API"
        return jsonify(swag)

    swagger_ui_blueprint = get_swaggerui_blueprint(
        os.getenv("SWAGGER_URL"),
        f'http://{os.getenv("SERVER_HOST")}:{os.getenv("SERVER_PORT")}/spec',
        config={
            'app_name': "Ticket System"
        }, )
    app.register_blueprint(swagger_ui_blueprint)
