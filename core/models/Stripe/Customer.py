import datetime as dt
from datetime import datetime

import stripe
from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import relationship

from core.extensions import db


def delete(id):
    return stripe.Customer.delete(id)


class Customer(db.Model):
    __tablename__ = 'stripe_customer'

    id = db.Column('customer_id', db.Integer, primary_key=True)

    stripe_id = db.Column('stripe_id', db.String, unique=True)

    created_at = db.Column(TIMESTAMP(True), server_default=func.now())
    updated_at = db.Column(TIMESTAMP(True), server_default=func.now())

    user = relationship("User", uselist=False, backref="stripe_customer")
    user_id = db.Column('user_id', db.Integer)

    card_id = db.Column(db.String, unique=True)
    scheduler_id = db.Column(db.String, unique=True)

    def __init__(self, **kwargs):
        super(Customer, self).__init__(**kwargs)

    def get(self, _id):
        customer = Customer.query.filter_by(stripe_id=_id).first_or_404()
        stripe.Customer.retrieve(id)
        return customer

    def edit(self, _id, **kwargs):
        customer = Customer.query.filter_by(stripe_id=_id).first_or_404()

        stripe_customer = stripe.Customer.modify(
            id,
            **kwargs,
        )
        print(stripe_customer)
        #     Add edit for internal Customer
        return customer

    def delete(self, _id):
        customer = Customer.query.filter_by(stripe_id=_id).first_or_404()
        stripe_customer = stripe.Customer.delete(_id)
        print(stripe_customer)
        db.session.delete(customer)
        db.session.commit()

    def get_card(self, _id):
        customer = Customer.query.filter_by(stripe_id=_id).first_or_404()

        stripe_card = stripe.Customer.retrieve_source(
            customer.id,
            customer.default_source,
        )
        return stripe_card

    def delete_card(self, _id):
        customer = Customer.query.filter_by(stripe_id=_id).first_or_404()

        stripe_card = stripe.Customer.delete_source(
            customer.id,
            customer.default_source,
        )
        if stripe_card["deleted"]:
            customer.default_source = ""
            db.session.commit()
            return customer
        else:
            raise Exception('Error occured')

    def create_schedule(self, _id, items):
        customer = Customer.query.filter_by(stripe_id=_id).first_or_404()

        stripe.SubscriptionSchedule.create(
            customer=_id,
            start_date=datetime.now(
                dt.timezone.utc),
            end_behavior="release",
            phases=[
                {
                    "items": items,
                    "iterations": 12,
                    "trial_end": customer.trial_end
                },
            ],
        )

    def update_schedule(self):
        print("update schedule")

    def delete_schedule(self):
        print("delete schedule")
