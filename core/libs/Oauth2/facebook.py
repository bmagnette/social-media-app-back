import os
from base64 import b64encode

import requests
from flask import request

from core.libs.Oauth2.oauth import OAuthSignIn
from core.models.Social.account import MediaType


class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.authorize_url = 'https://www.facebook.com/v13.0/dialog/oauth'
        self.access_token_url = 'https://graph.facebook.com/v13.0/oauth/access_token'
        self.redirect_uri = os.environ["BACK_END_APP_URI"] + '/oauth/callback/facebook'
        self.base_uri = 'https://graph.facebook.com'

    def authorize(self, current_user):
        # Scope - https://developers.facebook.com/docs/permissions/reference/
        params = {
            'scope': 'email,public_profile,pages_manage_posts,pages_show_list,pages_read_engagement,publish_to_groups',
            'auth_type': 'rerequest',
            'client_id': self.consumer_id,
            'redirect_uri': self.redirect_uri,
            'state': self.generate_state_token(current_user),
        }
        resp = requests.get(self.authorize_url, params=params)
        resp.raise_for_status()
        return resp.url

    def callback(self):
        state = request.args["state"]

        access_token = self.get_access_token()
        # fb_info = self.get_user_info(access_token)
        # picture = self.get_picture(fb_info["id"], access_token)

        pages = self.get_pages(access_token)
        groups = self.get_groups(access_token)

        payload = {
            "accounts": [
                # {
                #     "social_type": MediaType.FACEBOOK.value,
                #     "social_id": fb_info["id"],
                #     "name": fb_info["name"],
                #     "profile_picture": '',
                #     "expired_in": 60 * 24 * 60 * 60,  # in seconds
                #     "access_token": access_token,
                #     "profile_img": picture
                # }
            ]
        }

        for page in pages["data"]:
            page_id, page_access_token, page_name = page["id"], page["access_token"], page["name"]
            picture = self.get_picture(page_id, page_access_token)
            payload["accounts"].append({
                "social_type": MediaType.FACEBOOK_PAGE.value,
                "social_id": page_id,
                "name": page_name,
                "profile_picture": '',
                "expired_in": 60 * 24 * 60 * 60,  # in seconds
                "access_token": page_access_token,
                "profile_img": picture
            })

        for group in groups["data"]:
            name, _id, icon = group["name"], group["id"], group["icon"]
            picture = self.get_picture(_id, access_token)
            payload["accounts"].append({
                "social_type": MediaType.FACEBOOK_GROUP.value,
                "social_id": _id,
                "name": name,
                "profile_picture": '',
                "access_token": access_token,
                "expired_in": 60 * 24 * 60 * 90,  # in seconds
                "profile_img": picture
            })

        return payload, state

    def get_user_info(self, access_token):
        resp = requests.get(
            f'{self.base_uri}/me?access_token={access_token}')
        resp.raise_for_status()
        return resp.json()

    def get_picture(self, user_id, access_token):
        resp = requests.get(
            f'{self.base_uri}/{user_id}/picture?access_token={access_token}')
        resp.raise_for_status()
        return b64encode(resp.content).decode()

    def get_pages(self, access_token):
        url = f"{self.base_uri}/v12.0/me/accounts?fields=name,access_token&access_token={access_token}"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    def get_page_access_token(self, page_id, access_token):
        url = f"{self.base_uri}/{page_id}?fields=access_token&access_token={access_token}"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    def get_groups(self, access_token):
        params = {
            "admin_only": True
        }
        url = f"{self.base_uri}/v12.0/me/groups?fields=name,icon&access_token={access_token}"
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_posts(self, _id, access_token):
        url = f"{self.base_uri}/{_id}/feed?access_token={access_token}"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    def post(self, account, message):
        url = f"{self.base_uri}/{account['social_id']}/feed?message={message}&access_token={account['access_token']}"
        resp = requests.post(url)
        resp.raise_for_status()
        return resp.json()["id"]

    def get_access_token(self):
        auth_code = request.args["code"]

        if not auth_code:
            raise Exception("Not good context to call it.")
        params = {
            'client_id': self.consumer_id,
            'client_secret': self.consumer_secret,
            'redirect_uri': self.redirect_uri,
            'code': auth_code
        }

        resp = requests.get(self.access_token_url, params=params)
        resp.raise_for_status()
        return resp.json()["access_token"]
