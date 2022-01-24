from flask import Blueprint, request

from core.extensions import db
from core.helpers.handlers import to_json, response_wrapper, login_required
from core.models.account import initiate_account, Account
from core.models.account_category import AccountCategory
from core.models.user import User

account_router = Blueprint('account', __name__)


@account_router.route("/account", methods=["POST"])
@login_required
def add_account(current_user: User):
    data = request.get_json()

    if data:
        existing_account = Account.query.filter_by(social_id=data["social_id"]).first()
        if existing_account:
            return {"message": "Un compte existe déjà"}, 400
        initiate_account(current_user, **data)
        return response_wrapper('message', "Le compte vient d'être associé.", 201)
    else:
        return {"message": "Error : Account is not created"}, 400


@account_router.route("/account/<_id>", methods=["PUT"])
@login_required
def edit_account(current_user: User, _id: int):
    """
    TO IMPLEMENT
    """


@account_router.route("/account/<_id>", methods=["DELETE"])
@login_required
def remove_account(current_user: User, _id: int):
    """
    Delete an account
    """
    account = Account.query.filter_by(id=_id).first_or_404()
    db.session.delete(account)
    db.session.commit()
    return response_wrapper('content', [], 200)


@account_router.route("/account/<_id>", methods=["GET"])
@login_required
def read_account(current_user: User, _id: int):
    account = Account.query.filter_by(id=_id).first_or_404()
    return to_json(account.__dict__), 200


@account_router.route("/accounts/orphan", methods=["GET"])
@login_required
def read_account_without_category(current_user: User):
    res = []
    accounts = [account for account in current_user.accounts if account.category is None]
    for account in accounts:
        res.append(to_json(account.__dict__))
    return response_wrapper('content', res, 200)


@account_router.route("/accounts", methods=["GET"])
@login_required
def read_accounts(current_user: User):
    res = []
    for account in current_user.accounts:
        category = AccountCategory.query.filter_by(id=account.category_id).first()
        temp_res = to_json(account.__dict__)
        if category:
            temp_res["category"] = to_json(category.__dict__)
        res.append(temp_res)
    return response_wrapper('content', res, 200)
