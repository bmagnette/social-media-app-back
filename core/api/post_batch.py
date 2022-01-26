from functools import partial

from flask import Blueprint, request

from core.helpers.handlers import login_required, to_json, response_wrapper
from core.libs.Social.post import send_message
from core.models.Social.account_category import AccountCategory
from core.models.Social.post import Post
from core.models.Social.post_batch import PostBatch
from core.extensions import db
from core.models.user import User

batch_router = Blueprint('batch', __name__)


@batch_router.route("/batch", methods=["POST"])
@partial(login_required, payment_required=True)
def add_batch(current_user: User):
    """
    Si le batch s'envoie tout de suite alors envoyer tout de suite
    Sinon enregistrer un Scheduler/Queue en attente.
    """
    data = request.get_json()
    batch = PostBatch(author_id=current_user.id)
    db.session.add(batch)
    db.session.commit()

    for account in data["accounts"]:
        res = send_message(current_user.id, account, data["message"])
        print(res)
        post = Post(
            batch_id=batch.id,
            account_id=account["id"],
            type=account["social_type"],
            message=data["message"],
            photo=''
        )
        db.session.add(post)
    db.session.commit()

    # if not data["isSchedule"]:
    #     for test in []:
    #         db.session.add()
    #         print(test)
    #
    #
    #     return {}, 201

    # TODO
    return {}, 200


@batch_router.route("/batch/<_id>", methods=["PUT"])
@partial(login_required)
def edit_batch(current_user: User, _id: int):
    """
    TO IMPLEMENT
    """


@batch_router.route("/batch/<_id>", methods=["DELETE"])
@partial(login_required)
def remove_batch(current_user: User, _id: int):
    batch = PostBatch.query.filter_by(id=_id).first_or_404()
    db.session.delete(batch)
    db.session.commit()
    return response_wrapper('content', [], 200)


@batch_router.route("/batch/<_id>", methods=["GET"])
@partial(login_required)
def read_batch(current_user: User, _id: int):
    batch = PostBatch.query.filter_by(id=_id).first_or_404()
    return to_json(batch.__dict__), 200


@batch_router.route("/batchs", methods=["GET"])
@partial(login_required)
def get_batchs(current_user: User):
    res = []
    batchs = PostBatch.query.filter_by(author_id=current_user.id).all()
    for batch in batchs:
        posts = Post.query.filter_by(batch_id=batch.id).all()
        temp_res = to_json(batch.__dict__)
        temp_res["posts"] = []
        for post in posts:
            category = AccountCategory.query.filter_by(id=post.account.category_id).first()
            if category:
                category = to_json(category.__dict__)
                temp_res["category"] = category

            post = to_json(post.__dict__)

            temp_res["posts"].append(post)
        res.append(temp_res)

    return response_wrapper('content', res, 200)
