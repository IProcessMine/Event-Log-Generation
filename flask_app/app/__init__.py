from flask import Flask
from flask_bootstrap import Bootstrap
from flask_app.config_init import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Bootstrap(app)
    with app.app_context():
        from . import routes  # Ensure routes are imported here
        from .routes import main
    app.register_blueprint(main)


    return app
