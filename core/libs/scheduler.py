from datetime import datetime

from core.models.Stripe.Customer import Customer
from core.models.account import MediaType
from core.models.post_batch import PostBatch
import stripe

# Vérifier que le check pour obtenir les posts est correct.
# Se connecter dans le scheduler
# Vérifier que le token n'est pas expiré avant l'envoi
from core.models.user import User


def post_cron(app):
    with app.app_context():
        today = datetime.utcnow().now()
        batches = PostBatch.query.filter(PostBatch.isScheduled is True,
                                         PostBatch.schedule_date == today.timestamp(),
                                         PostBatch.schedule_hour == today.hour,
                                         PostBatch.schedule_minute == today.minute).all()
        app.logger.info(f"Running [{len(batches)}] - {today.hour}:{today.minute}")

        for batch in batches:
            for post in batch.posts:
                account, _type, token, expiry = post.account, post.type, post.token, post.expiry
                print(account, _type, token, expiry)
                if MediaType.LINKEDIN == _type:
                    print("SEND VIA LINKEDIN")
                elif MediaType.FACEBOOK == _type:
                    print("SEND VIA FACEBOOK")
                elif MediaType.INSTAGRAM == _type:
                    print("SEND VIA INSTAGRAM")
                elif MediaType.TWITTER == _type:
                    print("SEND VIA TWITTER")


def stripe_update(app):
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
