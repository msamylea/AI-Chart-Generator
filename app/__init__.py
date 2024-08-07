from flask import Flask
from app import config


def create_app(config_class=config.Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.api.routes import main
    app.register_blueprint(main)

    return app