from core.extensions import db


class StripeSubscription:
    id = db.Column('subscription_id', db.Integer, primary_key=True)
