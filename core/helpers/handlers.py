import json
from enum import Enum
from functools import wraps

import jwt
from flask import make_response, request, jsonify, current_app
from requests.exceptions import HTTPError
from sqlalchemy.orm.state import InstanceState
from werkzeug.exceptions import HTTPException

from core.models.account import MediaType, Account
from core.models.user import User
from datetime import datetime

def errors_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        app.logger.error(str(e))

        response = e.get_response()
        # replace the body with JSON
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })
        response.content_type = "application/json"
        return response

    @app.errorhandler(500)
    def not_found(error):
        app.logger.error(str(error))
        return {"message": error}, 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException) or isinstance(e, HTTPError):
            app.logger.error(str(e))
            return {"message": str(e)}, 500


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


def login_required(f):
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
        return f(current_user, *args, **kwargs)

    return decorated
