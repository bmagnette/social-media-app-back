from datetime import datetime
from functools import partial

from flask import Blueprint, request, current_app

from core.extensions import db
from core.helpers.handlers import login_required, to_json, response_wrapper
from core.libs.Oauth2.oauth import OAuthSignIn
from core.models.Social.account_category import AccountCategory
from core.models.Social.post import Post
from core.models.Social.post_batch import PostBatch
from core.models.user import User, UserType

batch_router = Blueprint('batch', __name__)


@batch_router.route("/batch", methods=["POST"])
@partial(login_required, payment_required=True)
def add_batch(current_user: User):
    """
    Si le batch s'envoie tout de suite alors envoyer tout de suite
    Sinon enregistrer un Scheduler/Queue en attente.
    """
    data = request.get_json()

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
    msg = "Message scheduled !" if "isScheduling" in data else 'Message sent'
    return response_wrapper('message', msg, 201)


@batch_router.route("/batch/bulk_upload", methods=["POST"])
@partial(login_required, payment_required=True)
def bulk_batch(current_user: User):
    """
    Bulk upload
    """
    data = request.get_json()

    for message in data["messages"]:
        batch_params = {
            "author_id": current_user.id,
            "isScheduled": True,
            "schedule_date": datetime.strptime(message['date'], '%d/%m/%Y %H:%M:%S'),
        }

        batch = PostBatch(**batch_params)

        db.session.add(batch)
        db.session.commit()

        post = Post(
            batch_id=batch.id,
            account_id=message["account"]["id"],
            type=message["account"]["social_type"],
            social_id=message["account"]["social_id"],
            message=message["content"],
            photo=message["image_url"]
        )
        db.session.add(post)
        current_app.logger.info(f'{current_user.id} - Adding new message from BATCH {post.type}')
        db.session.commit()
    return response_wrapper('message', 'Messages scheduled !', 201)


@batch_router.route("/batch/bulk", methods=["POST"])
@partial(login_required, payment_required=True)
def bulk_file(current_user: User):
    file = request.files["file"]
    res = []
    if file:
        file_data = file.read().decode("utf-8")
        lines = file_data.split("\n")
        line_index = 1

        for line in lines[:-1]:
            fields = line.split(",")

            try:
                date, message, image_url = fields
                image_url = image_url.replace('\r', '').replace(" ", '')
            except ValueError:
                return response_wrapper('message', f"Line {line_index} is missing required information.", 400)

            res.append({"id": line_index, "date": date, 'content': message, 'image_url': image_url})
            line_index += 1
        return response_wrapper('data', res, 200)
    else:
        return response_wrapper('message', "Missing file", 404)


@batch_router.route("/batch/<_id>", methods=["PUT"])
@partial(login_required)
def edit_batch(current_user: User, _id: int):
    """
    TO IMPLEMENT
    """


@batch_router.route("/batch/<_id>", methods=["DELETE"])
@partial(login_required)
def remove_batch(current_user: User, _id: int):
    posts = Post.query.filter_by(batch_id=_id).all()
    batch = PostBatch.query.filter_by(id=_id).first_or_404()

    for post in posts:
        db.session.delete(post)

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
    batchs = []

    admin_id = current_user.id if current_user.user_type == UserType.ADMIN else current_user.admin_id
    users = User.query.filter_by(admin_id=admin_id).all()
    admin_batch = PostBatch.query.filter_by(author_id=admin_id).all()

    id_list = [user.id for user in users]
    batchs.extend(admin_batch)
    for _id in id_list:
        user_batch = PostBatch.query.filter_by(author_id=_id).all()
        batchs.extend(user_batch)

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
