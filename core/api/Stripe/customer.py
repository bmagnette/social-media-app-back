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

        customer = Customer.query.filter_by(id=current_user.customer_id).first_or_404()

        if customer.card_id:
            return response_wrapper('message', 'Not implemented yet.', 400)

        customer.card_id = token["card"]["id"]

        stripe.Customer.modify(
            customer.stripe_id,
            metadata={"source": token["id"]},
        )

        return response_wrapper('message', 'Card added with success ! ', 201)
    except Exception as e:
        logger.error(str(e))
        return response_wrapper('message', str(e), 500)
