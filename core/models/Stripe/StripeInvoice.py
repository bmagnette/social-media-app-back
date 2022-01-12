from core.extensions import db


class StripeInvoice:
    id = db.Column('invoice_id', db.Integer, primary_key=True)
