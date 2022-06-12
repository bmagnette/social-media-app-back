import datetime as dt
from datetime import datetime

import sqlalchemy
from flask import current_app, render_template

from core.helpers.handlers import to_json
from core.libs.Oauth2.oauth import OAuthSignIn
from core.libs.mailer import send_email
from core.models.calendar_event import CalendarEvent
from core.models.Stripe.Customer import Customer
# Vérifier que le check pour obtenir les posts est correct.
# Se connecter dans le scheduler
# Vérifier que le token n'est pas expiré avant l'envoi
from core.models.user import User


def post_cron(app):
    """
    Each minute check if we should send Post.
    """
    with app.app_context():
        today = datetime.now(dt.timezone.utc)

        events = CalendarEvent.query.filter(CalendarEvent.isScheduled == True,
                                         sqlalchemy.extract('year', CalendarEvent.schedule_date) == today.year,
                                         sqlalchemy.extract('month', CalendarEvent.schedule_date) == today.month,
                                         sqlalchemy.extract('day', CalendarEvent.schedule_date) == today.day,
                                         sqlalchemy.extract('hour', CalendarEvent.schedule_date) == today.hour,
                                         sqlalchemy.extract('minute', CalendarEvent.schedule_date) == today.minute,
                                         ).all()
        app.logger.info(f"Running [{len(events)}] - {today.hour}:{today.minute}")

        for event in events:
            for post in event.posts:
                _type = post.type.lower()
                OAuthSignIn.get_provider(_type).post(post.account, post.message, post.media_link)
                app.logger.info(f"Sent one cron")


def stripe_update(app):
    """
    Update every day stripe account, to match usage with invoicing.
    """
    with app.app_context():
        users = User.query.filter_by(admin_id=None).all()
        app.logger.info(f"Cron - Stripe Update subscription")

        for user in users:
            customer = Customer.query.filter_by(user_id=user.id).first_or_404()
            customer.update_sub(user)
            app.logger.info(f"Stripe Update for {user.last_name}")

        app.logger.info(f"Cron - Stripe Update subscription ended")


def end_of_trial_email(app):
    with app.app_context():
        users = User.query.all()
        now = datetime.now()
        for user in users:
            end_free_trial_year = user.get_end_free_trial().year
            end_free_trial_month = user.get_end_free_trial().month
            end_free_trial_day = user.get_end_free_trial().day

            if end_free_trial_year == now.year and end_free_trial_month == now.month:
                if end_free_trial_day == now.day:
                    send_email("Your CronShot.com trial has ended", current_app.config['MAIL_DEFAULT_SENDER'],
                               [user.email],
                               render_template('mail/end_free_trial.html', user=user))
                    app.logger.info(f"Sending email end trial")

                if (now + dt.timedelta(days=2)).day == user.get_end_free_trial().day:
                    send_email("Your CronShot.com trial is ending in 2 days", current_app.config['MAIL_DEFAULT_SENDER'],
                               [user.email],
                               render_template('mail/last_48_end_free_trial.html', user=user))
                    app.logger.info(f"Sending email end trial in 2 days")
