from datetime import datetime

from core.models.account import MediaType
from core.models.post_batch import PostBatch


# Vérifier que le check pour obtenir les posts est correct.
# Se connecter dans le scheduler
# Vérifier que le token n'est pas expiré avant l'envoi
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


def stripe_update():
    print("Need to update Stripe subscribe")