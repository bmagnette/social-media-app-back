import base64
import json
import os

import requests
from flask import request, current_app
from sqlalchemy import func

from core.extensions import db
from core.libs.Oauth2.oauth import OAuthSignIn
from core.models.Social.account import MediaType, Account


class TwitterSignIn(OAuthSignIn):
    def __init__(self):
        super(TwitterSignIn, self).__init__('twitter')
        self.authorize_url = 'https://twitter.com/i/oauth2/authorize'
        self.access_token_url = 'https://api.twitter.com/2/oauth2/token'
        self.redirect_uri = os.environ["BACK_END_APP_URI"] + '/oauth/callback/twitter'
        self.base_uri = 'https://api.twitter.com'

    def authorize(self, current_user):
        # To see which scope correspond with routes.
        # https://developer.twitter.com/en/docs/authentication/guides/v2-authentication-mapping
        params = {
            "response_type": 'code',
            'client_id': self.consumer_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'tweet.read offline.access users.read tweet.write',
            'state': self.generate_state_token(current_user),
            'code_challenge': 'yiqkuflbqmdqn',
            'code_challenge_method': 'plain'
        }

        resp = requests.get(self.authorize_url, params=params)
        resp.raise_for_status()
        return resp.url

    def get_access_token(self, auth_code):
        base64_token = base64.b64encode(f"{self.consumer_id}:{self.consumer_secret}".encode('utf-8'))
        header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            "Authorization": f"Basic {base64_token.decode('utf-8')}",
        }

        payload = {
            'client_id': self.consumer_id,
            'code': auth_code,
            'code_verifier': 'yiqkuflbqmdqn',
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
        }

        resp = requests.post(self.access_token_url, data=payload, headers=header)
        resp.raise_for_status()
        return resp.json()

    def callback(self):
        auth_code = request.args["code"]
        state = request.args["state"]

        resp = self.get_access_token(auth_code)
        twitter_info = self.get_user_info(resp["access_token"])

        payload = {
            "accounts": [
                {
                    "access_token": resp["access_token"],
                    "refresh_token": resp["refresh_token"],
                    "expired_in": 7200,
                    "profile_picture": "",
                    "social_id": twitter_info["data"]["id"],
                    "name": twitter_info["data"]["username"],
                    "social_type": MediaType.TWITTER.value
                }
            ]
        }

        return payload, state

    def get_user_info(self, access_token):
        header = {
            'Authorization': f'Bearer {access_token}'
        }
        resp = requests.get(self.base_uri + '/2/users/me', headers=header)
        resp.raise_for_status()
        return resp.json()

    def refresh_token(self, refresh_token):
        """
        Refresh token on 401.
        """
        base64_token = base64.b64encode(f"{self.consumer_id}:{self.consumer_secret}".encode('utf-8'))

        header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            "Authorization": f"Basic {base64_token.decode('utf-8')}",
        }

        payload = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "client_id": self.consumer_id
        }

        resp = requests.post(self.access_token_url, data=payload, headers=header)
        resp.raise_for_status()
        return resp.json()

    def post(self, account, message):
        def post_request(_token, _message):
            return requests.post(self.base_uri + '/2/tweets', json.dumps({
                'text': _message
            }), headers={
                'Authorization': f'Bearer {_token}',
                'Content-type': 'application/json'
            })

        resp = post_request(account["access_token"], message)
        if resp.status_code == 401:
            token = self.refresh_token(account["refresh_token"])
            account = Account.query.filter_by(id=account["id"]).first_or_404()
            account.refresh_token = token["refresh_token"]
            account.access_token = token["access_token"]
            account.created_at = func.now()
            db.session.merge(account)
            db.session.commit()
            current_app.logger.info(f'Refreshing token {account.type}')

            resp = post_request(token["access_token"], message)

        resp.raise_for_status()
        return resp.json()["data"]["id"]
