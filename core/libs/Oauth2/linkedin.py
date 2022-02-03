import webbrowser

import requests
from flask import request

from core.libs.Oauth2.oauth import OAuthSignIn
from core.models.Social.account import MediaType


class LinkedInSignIn(OAuthSignIn):
    def __init__(self):
        super(LinkedInSignIn, self).__init__('linkedin')
        self.authorize_url = 'https://www.linkedin.com/oauth/v2/authorization'
        self.access_token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        self.base_url = 'https://api.linkedin.com/v2'

    def authorize(self, current_user):
        params = {
            'response_type': 'code',
            'client_id': self.consumer_id,
            'redirect_uri': self.base_uri + '/oauth/callback/linkedin',
            'state': self.generate_state_token(current_user),
            'scope': 'r_liteprofile,r_emailaddress,w_member_social'
        }
        response = requests.get(self.authorize_url, params=params)
        return response.url

    def callback(self):
        auth_code = request.args["code"]
        state = request.args["state"]

        access_token = self.get_access_token(auth_code)
        linkedin_info = self.get_user(access_token)

        payload = {
            "social_type": MediaType.LINKEDIN.value,
            "social_id": linkedin_info["id"],
            "name": linkedin_info["localizedLastName"] + " " + linkedin_info["localizedFirstName"],
            "profile_picture": linkedin_info["profilePicture"]["displayImage"],
            "expired_in": 60 * 24 * 60 * 60,  # in seconds,
            "access_token": access_token
        }

        return payload, state

    def get_access_token(self, auth_code):
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.base_uri + '/oauth/callback/linkedin',
            'client_id': self.consumer_id,
            'client_secret': self.consumer_secret
        }

        response = requests.post(self.access_token_url, data=data, timeout=30)
        response.raise_for_status()
        response = response.json()
        return response['access_token']

    def refresh_token(self):
        pass

    def get_user(self, access_token):
        header = {
            'Authorization': f'Bearer {access_token}',
            'cache-control': 'no-cache',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        r = requests.get(self.base_url + '/me', headers=header)
        r.raise_for_status()
        return r.json()

    def post(self, access_token, payload):
        header = {
            'Authorization': f'Bearer {access_token}',
            'cache-control': 'no-cache',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        r = requests.post(self.base_url + "/ugcPosts", headers=header, json=payload)
        r.raise_for_status()
        return r.json()
