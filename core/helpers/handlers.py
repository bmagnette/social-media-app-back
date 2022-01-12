import json
from functools import wraps

import jwt
from flask import make_response, request, jsonify, current_app
from requests.exceptions import HTTPError
from sqlalchemy.orm.state import InstanceState
from werkzeug.exceptions import HTTPException

from core.models.account import MediaType
from core.models.user import User


def errors_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        print(str(error))
        return {"message": error}, 404

    @app.errorhandler(500)
    def not_found(error):
        print(str(error))
        return {"message": error}, 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException) or isinstance(e, HTTPError):
            print(str(e))
            return {"message": str(e)}, 500


def parsing_to_json(o):
    if isinstance(o, MediaType):
        o = o.value
    if isinstance(o, InstanceState):
        return None
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

    if 'social_type' in data:
        data["social_type"] = data["social_type"].value
    return data


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # token = ''
        # if 'Authorization' in request.headers:
        #     token = request.headers['Authorization']
        #
        # if not token:
        #     return jsonify({'message': 'Votre token de connexion est inexistant.'}), 401

        # try:
        #     data = jwt.decode(token, current_app.config['SECRET_KEY'])
        # except jwt.ExpiredSignatureError:
        #     return response_wrapper('message', "Votre session a expiré, reconnectez-vous !", 401)
        # except jwt.InvalidTokenError:
        #     return response_wrapper('message', "Un problème est survenu, veuillez-vous reconnecter.", 401)

        current_user = User.query.filter_by(id=1).first_or_404()
        return f(current_user, *args, **kwargs)

    return decorated
