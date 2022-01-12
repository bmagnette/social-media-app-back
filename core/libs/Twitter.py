import webbrowser
from urllib.parse import quote

import requests

from core.helpers.auth import create_CSRF_token


class TwitterApi:
    APP_ID = '23011056'
    CONSUMER_KEY = '1soflnxtouOY2GCx2ZL761Z6z'
    CONSUMER_SECRET_KEY = 'gDIYpKzGWHJP0Sq1Ao3TFUhuwEC7gS97M4u8CcSepjqBxTWDlg'
    CLIENT_ID = 'cE01Um5ESnVJejg2UW1IUUktSlo6MTpjaQ'
    CLIENT_SECRET = '_DOuDrbvjj2fyS0gS3xgQGGBEFyOlTw4RRjNn5zc80XeGu_kDT'
    REDIRECT_URI = 'https://localhost:5000/linkedin/redirect-twitter'
    URI_AUTH = 'https://api.twitter.com/oauth'
    # URI_API = 'https://api.linkedin.com/v2'
    account = None

    def authorize(self):
        token = create_CSRF_token()
        params = {
            # 'response_type': 'code',
            # 'client_id': self.CLIENT_ID,
            # 'redirect_uri': self.REDIRECT_URI,
            # 'state': token,
            # 'scope': 'tweet.read,tweet.write,users.read',
            # 'challenge': 'challenge',
            # 'code_challenge_method': 'plain',
            'oauth_callback': self.REDIRECT_URI,
        }

        header = {
            'Authorization': f'OAuth oauth_consumer_key={self.CONSUMER_KEY}, oauth_nonce="$oauth_nonce", oauth_signature="oauth_signature", oauth_signature_method="HMAC-SHA1", oauth_timestamp="$timestamp", oauth_version="1.0"'
        }
        from pytwitter import Api
        api = Api(client_id=self.CLIENT_ID, oauth_flow=True)
        url, code_verifier, _ = api.get_oauth2_authorize_url()
        print(url, code_verifier)
        resp = api.generate_oauth2_access_token(url, code_verifier, self.REDIRECT_URI)
        print(resp)
        # response = requests.post(f'{self.URI_AUTH}/request_token', params=params, headers=header)
        # print(response.url)
        # webbrowser.open(response.url)
