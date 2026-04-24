from flask import Flask
from flask_cors import CORS

from app.config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    try:
        from app.api import register_routes
    except ModuleNotFoundError as exc:
        if exc.name != "app.api":
            raise
        register_routes = None

    if register_routes is not None:
        register_routes(app)

    return app
