import logging
from functools import partial

import stripe
from flask import request, Blueprint
from stripe.error import CardError
from datetime import datetime, timedelta
from core.extensions import db
from core.helpers.handlers import response_wrapper, login_required
from core.models.Stripe.Customer import Customer
from core.models.user import User

logger = logging.getLogger(__name__)

stripe_router = Blueprint('customer', __name__)


@stripe_router.route("/customer", methods=["POST"])
@partial(login_required)
def create_stripe_account(current_user: User):
    data = request.get_json()

    try:
        try:
            token = stripe.Token.create(
                card={
                    "number": data["creditCardNumber"],
                    "exp_month": int(data["expirationDate"][0:2]),
                    "exp_year": int("20" + data["expirationDate"][-2:]),
                    "cvc": data["CVC"],
                },
            )
        except CardError as e:
            return response_wrapper("message", e.error.message, 400)

        if current_user.customer_id:
            # Update card on user:
            customer = Customer.query.filter_by(id=current_user.customer_id).first_or_404()
            return response_wrapper('message', 'Not implemented yet.', 400)

        stripe_customer = stripe.Customer.create(description=current_user.email,
                                                 email=current_user.email,
                                                 source=token["id"])

        customer = Customer(stripe_id=stripe_customer["id"], user_id=current_user.id, card_id=token["card"]["id"])
        db.session.add(customer)
        db.session.commit()
        current_user.customer_id = customer.id
        db.session.commit()

        first_payment = int(current_user.get_end_free_trial().timestamp())
        if first_payment <= int(datetime.utcnow().timestamp()):
            first_payment = int((datetime.utcnow() + timedelta(days=1)).timestamp())

        sub = stripe.Subscription.create(
            customer=customer.stripe_id,
            billing_cycle_anchor=first_payment,
            trial_end=first_payment,
            billing_thresholds={
                "amount_gte": 5000
            },
            items=[
                {
                    "price": "price_1KK3v8GHalnQ9em2kXER9gwj",
                    "quantity": current_user.get_accounts(),
                },
                {
                    "price": "price_1KK3u2GHalnQ9em22sxu1rh9",
                    "quantity": current_user.get_users(),
                }
            ],
        )
        customer.scheduler_id = sub["id"]
        db.session.commit()

        return response_wrapper('message', 'Card added with success ! ', 201)
    except Exception as e:
        logger.error(str(e))
        return response_wrapper('message', str(e), 500)
