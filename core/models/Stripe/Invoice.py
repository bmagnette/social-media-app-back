from datetime import datetime
import enum

from core.extensions import db


class InvoiceStatus(enum.Enum):
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"


class Invoice(db.Model):
    __tablename__ = 'stripe_invoice'

    id = db.Column('invoice_id', db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    user = db.relationship('User', back_populates="invoices")

    created_at = db.Column(db.Float, default=datetime.utcnow().timestamp())
    updated_at = db.Column(db.Float, default=datetime.utcnow().timestamp())

    format_date = db.Column(db.String, nullable=False)

    amount_ht = db.Column(db.Float, nullable=False)
    amount_vat = db.Column(db.Float, nullable=False)
    amount_ttc = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(InvoiceStatus), nullable=False, default=InvoiceStatus.PENDING)


# class StripeItem(db.Model):
#     id = db.Column('item_id', db.Integer, primary_key=True)
#
#     created_at = db.Column(db.Float, default=datetime.utcnow().timestamp())
#     updated_at = db.Column(db.Float, default=datetime.utcnow().timestamp())
#
#     quantity = db.Column(db.Float, nullable=False)
#     label = db.Column(db.String, nullable=False)
#
#     unit_price = db.Column(db.String, nullable=False)
#
#     amount_ttc = db.Column(db.Float, nullable=False)
#     amount_ht = db.Column(db.Float, nullable=False)
#     amount_vat = db.Column(db.Float, nullable=False)
