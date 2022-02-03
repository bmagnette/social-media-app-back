import json
import os
import webbrowser
from functools import partial

import requests
from flask import Blueprint, redirect, make_response, current_app

from core.helpers.handlers import login_required
from core.libs.Oauth2.oauth import OAuthSignIn
from core.models.user import User

oauth = Blueprint('oauth', __name__)


@oauth.route('/authorize/<provider>', methods=["GET"])
@partial(login_required, payment_required=True)
def oauth_authorize(current_user: User, provider):
    url = OAuthSignIn(provider).get_provider(provider).authorize(current_user)
    response = make_response(redirect(url, code=302))
    response.headers = {
        'Authorization': 'whatever',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }
    current_app.logger.info(url)
    webbrowser.open_new(url)
    return {}, 200


@oauth.route('/callback/<provider>', methods=["GET"])
def oauth_callback(provider):
    payload, state = OAuthSignIn.get_provider(provider).callback()

    res = requests.post(os.environ["BACK_END_APP_URI"] + "/account",
                        data=json.dumps(payload),
                        headers={'Content-Type': 'application/json', 'Authorization': state})
    res.raise_for_status()

    return redirect(os.environ["FRONT_END_APP_URI"] + "/accounts")
