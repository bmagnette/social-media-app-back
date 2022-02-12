import datetime as dt
from datetime import datetime
from functools import partial

from flask import Blueprint, request, current_app

from core.extensions import db
from core.helpers.handlers import login_required, to_json, response_wrapper
from core.libs.Oauth2.oauth import OAuthSignIn
from core.models.Social.account_category import AccountCategory
from core.models.Social.post import Post
from core.models.Social.post_batch import PostBatch
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
    print(data)

    batch_params = {
        "author_id": current_user.id,
        "isScheduled": data["isScheduling"] if "isScheduling" in data else False,
        "schedule_date": datetime.fromisoformat(data["scheduleTime"][:-1]) if "isScheduling" in data else None,
    }
    batch = PostBatch(**batch_params)

    success_post_info = []
    for account in data["accounts"]:
        _id = None
        if "isScheduling" not in data:
            _id = OAuthSignIn.get_provider(account["social_type"].lower()).post(account, data["message"])

        success_post_info.append({
            "id": account["id"],
            "social_type": account["social_type"],
            "social_id": _id,
            "message": data["message"]
        })

    db.session.add(batch)
    db.session.commit()

    for post_info in success_post_info:
        post = Post(
            batch_id=batch.id,
            account_id=post_info["id"],
            type=post_info["social_type"],
            social_id=post_info["social_id"],
            message=post_info["message"],
            photo=''
        )
        db.session.add(post)
        current_app.logger.info(f'{current_user.id} - Adding new message {post.type}')

    db.session.commit()

    return response_wrapper('message', 'Message sent', 201)


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
