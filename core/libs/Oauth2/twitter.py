import base64
import webbrowser

import requests
from flask import request

from core.libs.Oauth2.oauth import OAuthSignIn
from core.models.Social.account import MediaType


class TwitterSignIn(OAuthSignIn):
    def __init__(self):
        super(TwitterSignIn, self).__init__('twitter')
        self.authorize_url = 'https://twitter.com/i/oauth2/authorize'
        self.access_token_url = 'https://api.twitter.com/2/oauth2/token'
        self.redirect_uri = 'http://localhost:5000/oauth/callback/twitter'
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
        webbrowser.open(resp.url)
        return

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
            "access_token": resp["access_token"],
            "refresh_token": resp["refresh_token"],
            "expired_in": 7200,
            "profile_picture": "",
            "social_id": twitter_info["data"]["id"],
            "name": twitter_info["data"]["username"],
            "social_type": MediaType.TWITTER.value
        }

        return payload, state

    def get_user_info(self, access_token):
        header = {
            'Authorization': f'Bearer {access_token}'
        }
        resp = requests.get(self.base_uri + '/2/users/me', headers=header)
        resp.raise_for_status()
        return resp.json()

    def refresh_token(self):
        """
        TO IMPLEMENT
        """
