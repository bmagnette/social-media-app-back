import webbrowser

import requests

from core.helpers.auth import create_CSRF_token, headers_bearer


class LinkedInAPI:
    CLIENT_ID = '77kwpo7k3bxgl1'
    CLIENT_SECRET = 'ASwtC0s53qiPTj2W'
    REDIRECT_URI = 'http://localhost:5000/linkedin/redirect-linkedin'
    URI_AUTH = 'https://www.linkedin.com/oauth/v2'
    URI_API = 'https://api.linkedin.com/v2'
    account = None

    def user_info(self, token):
        """
        Get user information from Linkedin
        """
        r = requests.get(self.URI_API + '/me', headers=headers_bearer(token))
        r.raise_for_status()
        return r.json()

    def authorize(self):
        """
        Make a HTTP request to the authorization URL.
        It will open the authentication URL.
        Once authorized, it'll redirect to the redirect URI given.
        The page will look like an error. but it is not.
        You'll need to copy the redirected URL.
        """
        token = create_CSRF_token()
        params = {
            'response_type': 'code',
            'client_id': self.CLIENT_ID,
            'redirect_uri': self.REDIRECT_URI,
            'state': token,
            'scope': 'r_liteprofile,r_emailaddress,w_member_social'
        }
        response = requests.get(f'{self.URI_AUTH}/authorization', params=params)
        webbrowser.open(response.url)

    def refresh_token(self, auth_code):
        """
        Exchange a Refresh Token for a New Access Token.
        """
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.REDIRECT_URI,
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET
        }

        response = requests.post(self.URI_AUTH + '/accessToken', data=data, timeout=30)
        response.raise_for_status()
        response = response.json()
        return response['access_token']

    def write_post(self, token, payload):
        if not self.account.token:
            refreshed_token = self.refresh_token(token)
        else:
            refreshed_token = self.account.token

        r = requests.post(self.URI_API + "/ugcPosts", headers=headers_bearer(refreshed_token), json=payload)
        r.raise_for_status()
        return r.json()


def parse_redirect_uri(redirect_response):
    """
    Parse redirect response into components.
    Extract the authorized token from the redirect uri.
    """
    from urllib.parse import urlparse, parse_qs

    url = urlparse(redirect_response)
    url = parse_qs(url.query)
    return url['code'][0]
