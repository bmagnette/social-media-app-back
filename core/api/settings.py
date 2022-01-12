from flask import Blueprint

from core.helpers.handlers import login_required
from core.models.user import User

setting_router = Blueprint('settings', __name__)


@setting_router.route("/calculate-price", methods=["GET"])
@login_required
def calculate_price(current_user: User):
    """
    Calculate subscription price
    """
    user = User.query.filter_by(id=current_user.id).first_or_404()

    nb_accounts = len(user.accounts)
    print(nb_accounts)
    return {"message": "Erreur : Aucun compte n'a été associé"}, 400
