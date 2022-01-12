from flask import Blueprint, request

from core.extensions import db
from core.helpers.handlers import login_required, to_json, response_wrapper
from core.models.account import Account
from core.models.account_category import AccountCategory, initiate_account_category
from core.models.user import User

category_router = Blueprint('category', __name__)


@category_router.route("/category", methods=["POST"])
@login_required
def add_category(current_user: User):
    data = request.get_json()
    if data:
        existing_account = AccountCategory.query.filter_by(label=data["categoryName"]).first()
        if existing_account:
            return {"message": "Un compte existe déjà"}, 400
        initiate_account_category(current_user, data)
        return {"message": "La catégorie vient d'être créer."}, 201
    else:
        return {"message": "Erreur : Aucune catégorie n'a été associé"}, 400


@category_router.route("/category/<_id>", methods=["PUT"])
@login_required
def edit_category(current_user: User, _id: int):
    data = request.get_json()
    category = AccountCategory.query.filter_by(id=_id).first_or_404()
    category.label = data["categoryName"]
    category.description = data["categoryDescription"]

    db.session.commit()
    return {}, 200


@category_router.route("/category/<_id>", methods=["DELETE"])
@login_required
def remove_category(current_user: User, _id: int):
    category = AccountCategory.query.filter_by(id=_id).first_or_404()
    db.session.delete(category)
    db.session.commit()
    return response_wrapper('content', [], 200)


@category_router.route("/category/<_id>", methods=["GET"])
@login_required
def read_category(current_user: User, _id: int):
    category = AccountCategory.query.filter_by(id=_id).first_or_404()
    return response_wrapper('content', to_json(category.__dict__), 200)


@category_router.route("/category/<_id>/accounts", methods=["GET"])
@login_required
def read_category_accounts(current_user: User, _id: int):
    category = AccountCategory.query.filter_by(id=_id).first_or_404()
    res = []
    for account in category.accounts:
        res.append(to_json(account.__dict__))
    return response_wrapper('content', res, 200)


@category_router.route("/categories", methods=["GET"])
@login_required
def read_categories(current_user: User):
    res = []
    for category in current_user.categories:
        temp_accounts = []
        temp_res = to_json(category.__dict__)
        for account in Account.query.filter_by(category_id=category.id).all():
            temp_accounts.append(to_json(account.__dict__))
        temp_res["accounts"] = temp_accounts
        res.append(temp_res)
    return response_wrapper('content', res, 200)
