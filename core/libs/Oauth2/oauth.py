import base64
import datetime as dt
import os
from datetime import datetime, timedelta

import jwt
import requests
from flask import current_app, url_for


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]

        self.time_out = 30
        self.provider_name = provider_name
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']
        self.base_uri = os.environ['BACK_END_APP_URI']

    def authorize(self, current_user):
        pass

    def callback(self):
        pass

    def generate_state_token(self, current_user):
        return jwt.encode({'id': current_user.id, 'exp': datetime.now(
                dt.timezone.utc) + timedelta(minutes=self.time_out)},
                          current_app.config['SECRET_KEY'])

    def get_callback_url(self):
        return url_for('oauth.oauth_callback', provider=self.provider_name, _external=True)

    @staticmethod
    def get_as_base64(url):
        return base64.b64encode(requests.get(url).content)

    @classmethod
    def get_provider(self, provider_name):
        from .twitter import TwitterSignIn
        from .facebook import FacebookSignIn
        from .linkedin import LinkedInSignIn

        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        provider_name = "facebook" if provider_name in ["facebook_page", "facebook_group"] else provider_name
        return self.providers[provider_name]
