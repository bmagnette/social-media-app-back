import json
from datetime import datetime
from enum import Enum
from functools import wraps

import jwt
from flask import make_response, request, jsonify, current_app
from requests.exceptions import HTTPError
from sqlalchemy.orm.state import InstanceState

from core.models.Social.account import Account
from core.models.user import User


def errors_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        app.logger.error(e.name + " - " + e.description)
        return response_wrapper("message", e.name + " - " + e.description, 404)

    @app.errorhandler(500)
    def not_found(e):
        app.logger.error(e.name + " - " + e.description)
        return response_wrapper("message", e.name + " - " + e.description, 500)

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPError):
            app.logger.error(f'{e.response.status_code} - {e.response.json()["error"]["message"]}')
            return response_wrapper('message', e.response.json()["error"]['message'], e.response.status_code)
        return response_wrapper('message', e.name + " - " + e.description, e.response.status_code)


def parsing_to_json(o):
    if isinstance(o, Enum):
        return o.value
    if isinstance(o, InstanceState):
        return None
    if isinstance(o, Account):
        return o.__dict__
    if isinstance(o, datetime):
        return datetime.timestamp(o)
    return o


def response_wrapper(content_type, content, http_code):
    resp = make_response(json.dumps({content_type: content}, default=parsing_to_json), http_code)
    resp.headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'}
    return resp


def to_json(data):
    if '_sa_instance_state' in data:
        del data["_sa_instance_state"]
    return data


def login_required(f, payment_required=False):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = ''
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return jsonify({'message': "Your token access doesn't work, connect your account again."}), 401

        try:
            data = jwt.decode(token.encode('UTF-8'), current_app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return response_wrapper('message', "Your session has expired, log in again!", 401)
        except jwt.InvalidTokenError:
            return response_wrapper('message', "Something went wrong, please log in again.", 401)

        current_user = User.query.filter_by(id=data["id"]).first_or_404()

        if payment_required and not current_user.customer_id and current_user.get_end_free_trial() < datetime.utcnow():
            return response_wrapper('message', 'Payment Required, update your card info.', 402)

        return f(current_user, *args, **kwargs)

    return decorated
