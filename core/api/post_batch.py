from flask import Blueprint, request

from core.helpers.handlers import login_required
from core.libs.post import send_message
from core.models.post import Post
from core.models.post_batch import PostBatch
from core.extensions import db
from core.models.user import User

batch_router = Blueprint('batch', __name__)


@batch_router.route("/batch", methods=["POST"])
@login_required
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
@login_required
def edit_batch(current_user: User, _id: int):
    """
    TO IMPLEMENT
    """


@batch_router.route("/batch/<_id>", methods=["DELETE"])
@login_required
def remove_batch(current_user: User, _id: int):
    """
    TO IMPLEMENT
    """


@batch_router.route("/batch/<_id>", methods=["GET"])
@login_required
def read_batch(current_user: User, _id: int):
    """
    TO IMPLEMENT
    """


@batch_router.route("/categories/<_id>", methods=["GET"])
@login_required
def read_categories(current_user: User, _id: int):
    print("")
