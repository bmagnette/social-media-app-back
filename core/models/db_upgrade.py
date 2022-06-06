import os

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate

import sys
from pathlib import Path

sys.path.append("C://Users/baptiste/social-media-scheduler/social-media-scheduler-back")
from core.extensions import db


def create_app():
    dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
    load_dotenv(dotenv_path=str(dir_path.parent.parent) + '/.env')

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI_PROD"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

    db.init_app(app)

    with app.app_context():
        db.create_all()

    Migrate(app, db)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
