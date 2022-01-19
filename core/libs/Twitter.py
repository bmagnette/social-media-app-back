import hashlib
import hmac
import time
import urllib.parse as urlparse
import webbrowser

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
            "oauth_nonce": "kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg",
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_token": oauth_token,
            "oauth_version": "1.0",
            "status": message
        }

        parameters = {
            "include_entities": True,
            "oauth_consumer_key": "xvz1evFS4wEEPTGEFPHBog",
            "oauth_nonce": "kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg",
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": "1318622958",
            "oauth_token": "370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb",
            "oauth_version": "1.0",
            "status": 'Hello Ladies + Gentlemen, a signed OAuth request!'
        }

        base_string = "%s&%s&%s" % (
            "POST", urlparse.quote(url, ""), urlparse.quote('&'.join(sorted("%s=%s" % (key, value)
                                                                            for key, value in
                                                                            parameters.items())),
                                                            ""))

        # Create the signature using signing key composed of consumer secret and token secret obtained during 3-legged dance
        key = f'{urlparse.quote(self.CONSUMER_SECRET_KEY, "")}&{urlparse.quote(oauth_token_secret, "")}'
        key = "kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw&LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE"
        signature = hmac.new(bytes(key, 'UTF-8'), bytes(base_string, 'UTF-8'), hashlib.sha1).digest()
        print(signature)
        import base64
        # Add result to parameters and create a string in required format for header
        parameters['oauth_signature'] = "hCtSmYh+iHYCEqBWrE7C7hYmtUk="
        print(parameters["oauth_signature"])
        auth_header = 'OAuth %s' % ', '.join(sorted('%s="%s"' % (urlparse.quote(key, ""), urlparse.quote(value, ""))
                                                    for key, value in parameters.items() if key != 'status'))

        # Set HTTP headers
        http_headers = {"Authorization": auth_header, 'Content-Type': 'application/x-www-form-urlencoded'}

        # Send the request
        response = requests.post(url, message, headers=http_headers)

        # Set messages that will be used in modal dialogs
        if response.status_code == 200:
            print("Tweet sent mentioning")
        else:
            print("Error sending tweet: %s" % response.content)
        response.raise_for_status()
        return response.json()
