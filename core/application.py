import datetime as dt
import logging
import os
from datetime import datetime

import stripe
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from flask import Flask

from core.api.Stripe.customer import stripe_router
from core.api.account import account_router
from core.api.event import event_router
from core.api.category import category_router
from core.api.oauth2 import oauth
from core.api.unsplash.unsplash import unsplash
from core.api.user import auth
from core.extensions import mail, db, cors, scheduler, migrate
from core.helpers.handlers import errors_handlers
from core.libs.scheduler import stripe_update, post_cron, end_of_trial_email


def create_app() -> Flask:
    dir_path = os.path.dirname(os.path.realpath(__file__))

    project_path = os.path.abspath(os.path.join(dir_path, os.pardir))
    load_dotenv(dotenv_path=project_path + '/.env')
    logging.basicConfig(level=logging.ERROR, format=f'%(asctime)s %(levelname)s : %(message)s')

    app = Flask("Social Media APP", template_folder=os.path.join(dir_path, 'templates'))
    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(logging.INFO)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True if os.environ["env"] == 'dev' else False
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
    app.config["MAIL_SERVER"] = os.environ["GMAIL_SERVER"]
    app.config["MAIL_PORT"] = os.environ["GMAIL_PORT"]
    app.config["MAIL_PASSWORD"] = os.environ["GMAIL_PASSWORD"]
    app.config["MAIL_USERNAME"] = os.environ["GMAIL_EMAIL"]
    app.config["STRIPE_SECRET"] = os.environ["STRIPE_SECRET"]
    app.config['OAUTH_CREDENTIALS'] = {
        'facebook': {
            'id': os.environ["FACEBOOK_CLIENT_ID"],
            'secret': os.environ["FACEBOOK_CLIENT_SECRET"]
        },
        'twitter': {
            'id': os.environ["TWITTER_CLIENT_ID"],
            'secret': os.environ["TWITTER_CLIENT_SECRET"]
        },
        'linkedin': {
            'id': os.environ["LINKEDIN_CLIENT_ID"],
            'secret': os.environ["LINKEDIN_CLIENT_SECRET"],
        },
        'instagram': {
            'id': '',
            'secret': ''
        }
    }
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_DEFAULT_SENDER"] = ('CronShot', os.environ["GMAIL_EMAIL"])
    app.config["MAIL_ASCII_ATTACHMENTS "] = True
    stripe.api_key = os.environ["STRIPE_SECRET"]
    stripe.api_version = "2020-08-27"
    app.register_blueprint(oauth, url_prefix='/oauth')
    app.register_blueprint(auth)
    app.register_blueprint(account_router)
    app.register_blueprint(category_router)
    app.register_blueprint(event_router)
    app.register_blueprint(unsplash)

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
    migrate.init_app(app, db)


def register_schedulers(app: Flask) -> None:
    if os.environ["env"] != "dev":
        with app.app_context():
            scheduler.start()
        scheduler.add_job(end_of_trial_email, 'interval', [app], hours=24,
                          next_run_time=(datetime.now(dt.timezone.utc)))

        scheduler.add_job(post_cron, 'interval', [app], seconds=60,
                          next_run_time=(datetime.now(dt.timezone.utc) + relativedelta(minutes=+1)).replace(second=0))
        scheduler.add_job(stripe_update, 'interval', [app], hours=24,
                          next_run_time=datetime.now(
                              dt.timezone.utc).replace(hour=0, minute=30))


def register_models(app: Flask) -> None:
    with app.app_context():
        # db.drop_all()
        db.create_all()
