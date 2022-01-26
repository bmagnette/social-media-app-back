import logging
import os
from datetime import datetime

import stripe
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate

from core.api.Stripe.customer import stripe_router
from core.api.Stripe.invoices import invoice_router
from core.api.account import account_router
from core.api.category import category_router
from core.api.oauth2 import oauth2_router
from core.api.post_batch import batch_router
from core.api.user import auth
from core.extensions import mail, db, cors, scheduler
from core.helpers.handlers import errors_handlers
from core.libs.scheduler import post_cron, stripe_update


def create_app() -> Flask:
    dir_path = os.path.dirname(os.path.realpath(__file__))

    project_path = os.path.abspath(os.path.join(dir_path, os.pardir))
    load_dotenv(dotenv_path=project_path + '/.env')
    logging.basicConfig(level=logging.ERROR, format=f'%(asctime)s %(levelname)s : %(message)s')
    app = Flask("Social Media APP", template_folder=os.path.join(dir_path, 'templates'))
    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(logging.INFO)
    app.logger.info('this will show in the log')

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True if os.environ["env"] == 'dev' else False
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
    app.config["MAIL_SERVER"] = os.environ["GMAIL_SERVER"]
    app.config["MAIL_PORT"] = os.environ["GMAIL_PORT"]
    app.config["MAIL_PASSWORD"] = os.environ["GMAIL_PASSWORD"]
    app.config["MAIL_USERNAME"] = os.environ["GMAIL_EMAIL"]
    app.config["STRIPE_SECRET"] = os.environ["STRIPE_SECRET"]
    app.config["LINKEDIN_CLIENT_ID"] = os.environ["LINKEDIN_CLIENT_ID"]
    app.config["LINKEDIN_CLIENT_SECRET"] = os.environ["LINKEDIN_CLIENT_SECRET"]
    app.config["LINKEDIN_REDIRECT_URI"] = os.environ["LINKEDIN_REDIRECT_URI"]

    app.config["MAIL_USE_TLS"] = False
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_DEFAULT_SENDER"] = os.environ["GMAIL_EMAIL"]
    app.config["MAIL_ASCII_ATTACHMENTS "] = True
    stripe.api_key = os.environ["STRIPE_SECRET"]
    app.register_blueprint(oauth2_router, url_prefix='/linkedin')
    app.register_blueprint(auth)
    app.register_blueprint(account_router)
    app.register_blueprint(invoice_router)
    app.register_blueprint(category_router)
    app.register_blueprint(batch_router)
    app.register_blueprint(stripe_router, url_prefix='/stripe')

    errors_handlers(app)
    register_extensions(app)
    register_models(app)
    register_schedulers(app)

    return app


def register_extensions(app: Flask) -> None:
    mail.init_app(app)
    db.init_app(app)
    cors.init_app(app)
    Migrate(app, db)


def register_schedulers(app: Flask) -> None:
    with app.app_context():
        scheduler.start()

    scheduler.add_job(post_cron, 'interval', [app], seconds=60,
                      next_run_time=(datetime.utcnow() + relativedelta(minutes=+1)).replace(second=0))
    scheduler.add_job(stripe_update, 'interval', [app], hours=24,
                      next_run_time=datetime.utcnow().replace(hour=0, minute=30))


def register_models(app: Flask) -> None:
    with app.app_context():
        db.create_all()
