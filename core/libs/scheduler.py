import datetime as dt
from datetime import datetime

import sqlalchemy
import stripe
from flask import current_app, render_template

from core.helpers.handlers import to_json
from core.libs.Oauth2.oauth import OAuthSignIn
from core.libs.mailer import send_email
from core.models.Social.post_batch import PostBatch
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

        batches = PostBatch.query.filter(PostBatch.isScheduled == True,
                                         sqlalchemy.extract('year', PostBatch.schedule_date) == today.year,
                                         sqlalchemy.extract('month', PostBatch.schedule_date) == today.month,
                                         sqlalchemy.extract('day', PostBatch.schedule_date) == today.day,
                                         sqlalchemy.extract('hour', PostBatch.schedule_date) == today.hour,
                                         sqlalchemy.extract('minute', PostBatch.schedule_date) == today.minute,
                                         ).all()
        app.logger.info(f"Running [{len(batches)}] - {today.hour}:{today.minute}")

        for batch in batches:
            for post in batch.posts:
                _type = post.account.social_type.lower()
                OAuthSignIn(_type).get_provider(_type).post(to_json(post.account.__dict__), post.message)
                app.logger.info(f"Sent one cron")


def stripe_update(app):
    """
    Update every day stripe account, to match usage with invoicing.
    """
    with app.app_context():
        users = User.query.filter(User.customer_id is not None).all()
        app.logger.info(f"Cron - Stripe Update subscription")

        for user in users:
            customer = Customer.query.filter_by(user_id=user.id).first_or_404()

            sub = stripe.Subscription.retrieve(
                customer.scheduler_id,
            )

            for item in sub["items"]["data"]:
                stripe.SubscriptionItem.modify(
                    item["id"],
                    quantity=user.get_accounts(),
                )
            app.logger.info(f"Stripe Update")

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
