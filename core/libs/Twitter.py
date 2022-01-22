import base64
import hashlib
import hmac
import time
import urllib.parse as urlparse
import webbrowser
from random import random

import oauth2
import requests

from core.helpers.auth import create_CSRF_token

session_data = {}


class TwitterApi:
    APP_ID = '23011056'
    CONSUMER_KEY = '1soflnxtouOY2GCx2ZL761Z6z'
    CONSUMER_SECRET_KEY = 'gDIYpKzGWHJP0Sq1Ao3TFUhuwEC7gS97M4u8CcSepjqBxTWDlg'
    CLIENT_ID = 'cE01Um5ESnVJejg2UW1IUUktSlo6MTpjaQ'
    CLIENT_SECRET = '_DOuDrbvjj2fyS0gS3xgQGGBEFyOlTw4RRjNn5zc80XeGu_kDT'
    REDIRECT_URI = 'https://localhost:5000/linkedin/redirect-twitter'
    URI_AUTH = 'https://api.twitter.com/oauth/authorize'
    # URI_API = 'https://api.linkedin.com/v2'
    account = None

    def authorize(self, user_id):
        consumer = oauth2.Consumer(self.CONSUMER_KEY, self.CONSUMER_SECRET_KEY)
        resp, content = oauth2.Client(consumer).request('https://api.twitter.com/oauth/request_token', "GET")
        request_token = dict(urlparse.parse_qsl(content.decode('utf-8')))
        session_data[user_id] = {"oauth_token": request_token["oauth_token"],
                                 "oauth_token_secret": request_token["oauth_token_secret"]}
        # for this user need to save oauth token and secret.
        webbrowser.open(f"{self.URI_AUTH}?oauth_token={request_token['oauth_token']}")

    def callback(self, user_id, oauth_verifier):
        token = oauth2.Token(session_data[user_id]["oauth_token"], session_data[user_id]["oauth_token_secret"])
        token.set_verifier(oauth_verifier)

        # Create a new oauth2.Client object, wrapping both the consumer and token objects
        consumer = oauth2.Consumer(self.CONSUMER_KEY, self.CONSUMER_SECRET_KEY)
        client = oauth2.Client(consumer, token)

        resp, content = client.request('https://api.twitter.com/oauth/access_token', "POST")
        access_token = dict(urlparse.parse_qsl(content.decode('utf-8')))

        return access_token

    def post(self, oauth_token, oauth_token_secret, message):
        url = 'https://api.twitter.com/1.1/statuses/update.json'

        parameters = {
            "oauth_consumer_key": self.CONSUMER_KEY,
            "oauth_nonce": hashlib.sha1(str(random).encode("utf-8")).hexdigest(),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_token": oauth_token,
            "oauth_version": "1.0",
            "status": message,
            "x_auth_login_challenge": "1",
            "x_auth_login_verification": "1",
            "x_auth_mode": "client_auth",
        }

        base_string = "%s&%s&%s" % (
            "POST", urlparse.quote(url, ""), urlparse.quote('&'.join(sorted("%s=%s" % (key, value)
                                                                            for key, value in
                                                                            parameters.items())),
                                                            ""))

        # Create the signature using signing key composed of consumer secret and token secret obtained during 3-legged dance
        key = f'{urlparse.quote(self.CONSUMER_SECRET_KEY, "")}&{urlparse.quote(oauth_token_secret, "")}'
        signature = hmac.new(bytes(key, 'UTF-8'), bytes(base_string, 'UTF-8'), hashlib.sha1).digest()

        # Add result to parameters and create a string in required format for header
        parameters['oauth_signature'] = base64.b64encode(signature).decode()
        print(parameters["oauth_signature"])
        auth_header = 'OAuth %s' % ', '.join(sorted('%s="%s"' % (urlparse.quote(key, ""), urlparse.quote(value, ""))
                                                    for key, value in parameters.items() if key != 'status'))

        # Set HTTP headers
        http_headers = {"Authorization": auth_header, 'Content-Type': 'application/x-www-form-urlencoded'}
        print(http_headers)
        # Send the request
        response = requests.post(url, message, headers=http_headers)

        # Set messages that will be used in modal dialogs
        if response.status_code == 200:
            print("Tweet sent mentioning")

        response.raise_for_status()
        return response.json()
