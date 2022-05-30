from functools import partial

from flask import Blueprint, request

from core.extensions import db
from core.helpers.handlers import login_required, to_json, response_wrapper
from core.models.Social.account import Account
from core.models.Social.account_category import AccountCategory, initiate_account_category, CategoryGroup
from core.models.user import User

category_router = Blueprint('category', __name__)


@category_router.route("/category", methods=["POST"])
@partial(login_required, payment_required=True)
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
@partial(login_required)
def edit_category(current_user: User, _id: int):
    data = request.get_json()
    category = AccountCategory.query.filter_by(id=_id).first_or_404()
    category.accounts = []

    for account in data["accounts"]:
        acc = Account.query.filter_by(id=account["id"]).first_or_404()
        category.accounts.append(acc)
    category.label = data["categoryName"]
    category.color = data["color"]
    db.session.commit()
    return {}, 200


@category_router.route("/category/<_id>", methods=["DELETE"])
@partial(login_required)
def remove_category(current_user: User, _id: int):
    relationships = CategoryGroup.query.filter_by(category_id=_id).all()
    for relationship in relationships:
        db.session.delete(relationship)

    category = AccountCategory.query.filter_by(id=_id).first_or_404()
    db.session.delete(category)
    db.session.commit()
    return response_wrapper('content', [], 200)


@category_router.route("/category/<_id>", methods=["GET"])
@partial(login_required)
def read_category(current_user: User, _id: int):
    category = AccountCategory.query.filter_by(id=_id).first_or_404()
    return response_wrapper('content', to_json(category.__dict__), 200)


@category_router.route("/category/<_id>/accounts", methods=["GET"])
@partial(login_required)
def read_category_accounts(current_user: User, _id: int):
    category = AccountCategory.query.filter_by(id=_id).first_or_404()
    res = []
    for account in category.accounts:
        res.append(to_json(account.__dict__))
    return response_wrapper('content', res, 200)


@category_router.route("/categories", methods=["GET"])
@partial(login_required)
def read_categories(current_user: User):
    res = []

    for category in current_user.categories:
        right = CategoryGroup.query.filter_by(user_id=current_user.id, category_id=category.id).first_or_404()
        temp_accounts = []
        temp_res = category.__dict__
        for account in Account.query.filter_by(category_id=category.id).all():
            temp_accounts.append(to_json(account.__dict__))
        temp_res['right'] = right.__dict__
        temp_res["accounts"] = temp_accounts
        res.append(temp_res)
    return response_wrapper('content', res, 200)


@category_router.route("/categories/<user_id>", methods=["GET"])
@partial(login_required)
def read_categories_by_user(current_user: User, user_id):
    res = []

    for category in current_user.categories:
        right = CategoryGroup.query.filter_by(user_id=int(user_id), category_id=category.id).first()
        if right:
            temp_accounts = []
            temp_res = category.__dict__
            for account in Account.query.filter_by(category_id=category.id).all():
                temp_accounts.append(to_json(account.__dict__))
            temp_res['right'] = right.__dict__
            temp_res["accounts"] = temp_accounts
            res.append(temp_res)
    return response_wrapper('content', res, 200)
