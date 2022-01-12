from core.extensions import db


class StripeAccount:
    id = db.Column('stripe_account_id', db.Integer, primary_key=True)

    customer_id = db.Column(db.String, nullable=False)

    # Link to an user.
