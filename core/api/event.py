import base64
from datetime import datetime
from functools import partial

import requests
from flask import Blueprint, request, current_app

from core.extensions import db
from core.helpers.handlers import login_required, to_json, response_wrapper
from core.libs.AWS.file import upload_to_aws
from core.libs.Oauth2.oauth import OAuthSignIn
from core.models.Social.account_category import AccountCategory
from core.models.Social.post import Post, PostStatus
from core.models.calendar_event import CalendarEvent, EventType
from core.models.user import User, UserType

event_router = Blueprint('event', __name__)


def get_media_selections(image_URLs, post, current_user):
    """
    Return array of bytes from images with different types and upload it to aws.
    """
    if current_user.admin_id:
        current_user = User.query.filter_by(id=current_user.admin_id).first_or_404()

    media_urls, media_b64 = [], []
    for i in range(0, len(image_URLs), 1):
        image = image_URLs[i]
        if image.startswith("https"):
            # Transform temp url coming from another source to a personal source.
            resp = requests.get(url=image)
            extension = '.' + resp.headers["Content-Type"].split('/')[1]

            bucket = "multimedia-cronshot"
            file_name = f'{post.id}_{i}{extension}'

            if upload_to_aws('byte', resp.content, bucket, f'{current_user.id}/posts/{file_name}'):
                media_link = f"https://{bucket}.s3.eu-west-3.amazonaws.com/{current_user.id}/posts/{file_name}"
                media_urls.append(media_link)
                media_b64.append(base64.b64encode(resp.content))
        elif image.startswith("blob"):
            # Blob come directly from user computer. Transfer it to bytes and upload to aws.
            # TRANSFORM BLOB to Bytes and post it.
            print("TODO")
    return media_urls, media_b64


@event_router.route("/event", methods=["POST"])
@partial(login_required, payment_required=True)
def add_event(current_user: User):
    """
    Si l'event s'envoie tout de suite alors envoyer tout de suite
    Sinon enregistrer un Scheduler/Queue en attente.
    """
    data = request.get_json()

    event_params = {
        "author_id": current_user.id,
        "isScheduled": data["isScheduling"] if "isScheduling" in data else False,
        "schedule_date": datetime.fromisoformat(data["scheduleTime"][:-1]) if "isScheduling" in data else None,
    }

    event = CalendarEvent(event_type=EventType.POST, **event_params)
    db.session.add(event)
    db.session.commit()

    posts = []
    for _account in data["accounts"]:
        post = Post(
            event_id=event.id,
            account_id=_account["id"],
            type=_account["social_type"],
            social_id=_account["social_id"],
            message=data["message"],
            status=PostStatus.PROCESSING,
            media_b64=[],
            media_link=[],
        )
        db.session.add(post)
        posts.append(post)
        current_app.logger.info(f'{current_user.id} - Adding new message {post.type}')
    db.session.commit()

    for post in posts:
        _id = None
        media_urls, media_b64 = [], []
        if data["imageURLs"]:
            media_urls, media_b64 = get_media_selections(data["imageURLs"], post, current_user)

        if "isScheduling" not in data:
            _id = OAuthSignIn.get_provider(post.type.lower()).post(post.account, data["message"], media_urls)
            post.social_id = _id
            post.status = PostStatus.POSTED
        else:
            post.status = PostStatus.SCHEDULED

        post.media_link = media_urls
        post.media_b64 = media_b64
    db.session.commit()
    msg = "Message scheduled !" if "isScheduling" in data else 'Message sent'
    return response_wrapper('message', msg, 201)


@event_router.route("/event/bulk_upload", methods=["POST"])
@partial(login_required, payment_required=True)
def bulk_event(current_user: User):
    """
    Bulk upload
    """
    data = request.get_json()

    for message in data["messages"]:
        event_params = {
            "author_id": current_user.id,
            "isScheduled": True,
            "schedule_date": datetime.strptime(message['date'], '%d/%m/%Y %H:%M:%S'),
        }

        event = CalendarEvent(event_type=EventType.POST, **event_params)

        db.session.add(event)
        db.session.commit()

        post = Post(
            event_id=event.id,
            account_id=message["account"]["id"],
            type=message["account"]["social_type"],
            social_id=message["account"]["social_id"],
            message=message["content"],
            photo=message["image_url"]
        )
        db.session.add(post)
        current_app.logger.info(f'{current_user.id} - Adding new message from event {post.type}')
        db.session.commit()
    return response_wrapper('message', 'Messages scheduled !', 201)


@event_router.route("/event/bulk", methods=["POST"])
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


@event_router.route("/event/<_id>", methods=["PUT"])
@partial(login_required)
def edit_event(current_user: User, _id: int):
    """
    TO IMPLEMENT
    """
    data = request.get_json()

    # On ne peut pas mettre une date dans le passé.
    event = CalendarEvent.query.filter_by(id=_id).first_or_404()
    event.schedule_date = data["startDate"]
    event.isScheduled = True
    db.session.commit()
    return response_wrapper('message', "Missing file", 200)


@event_router.route("/event/<_id>", methods=["DELETE"])
@partial(login_required)
def remove_event(current_user: User, _id: int):
    posts = Post.query.filter_by(event_id=_id).all()
    event = CalendarEvent.query.filter_by(id=_id).first_or_404()

    for post in posts:
        db.session.delete(post)

    db.session.delete(event)
    db.session.commit()
    return response_wrapper('content', [], 200)


@event_router.route("/event/<_id>", methods=["GET"])
@partial(login_required)
def read_event(current_user: User, _id: int):
    event = CalendarEvent.query.filter_by(id=_id).first_or_404()
    return to_json(event.__dict__), 200


@event_router.route("/events", methods=["GET"])
@partial(login_required)
def get_events(current_user: User):
    res = []
    events = []

    admin_id = current_user.id if current_user.user_type == UserType.ADMIN else current_user.admin_id
    users = User.query.filter_by(admin_id=admin_id).all()
    admin_event = CalendarEvent.query.filter_by(author_id=admin_id).all()

    id_list = [user.id for user in users]
    events.extend(admin_event)
    for _id in id_list:
        user_event = CalendarEvent.query.filter_by(author_id=_id).all()
        events.extend(user_event)

    for event in events:
        posts = Post.query.filter_by(event_id=event.id).all()
        temp_res = to_json(event.__dict__)
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
