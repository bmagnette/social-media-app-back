from functools import partial

from flask import Blueprint

from core.helpers.handlers import to_json, response_wrapper, login_required
from core.models.Stripe.Invoice import Invoice
from core.models.user import User

invoices_router = Blueprint('invoices', __name__)


@invoices_router.route("/invoices", methods=["GET"])
@partial(login_required)
def read_invoices(current_user: User):
    res = []
    for invoice in Invoice.query.filter_by(user_id=current_user.id).all():
        res.append(to_json(invoice.__dict__))
    return response_wrapper('content', res, 200)