from flask import Flask
from config import Config
from extensions import db, login_manager
from auth import auth
from main import main
from models import User, Entry  # noqa: F401 (needed for db.create_all)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
