import webbrowser

import requests

from core.helpers.auth import create_CSRF_token


class FacebookLogin:
    CLIENT_ID = '661011595256018'
    CLIENT_SECRET = '4304f9a379f79bc0316efda3541db4cb'
    REDIRECT_URI = 'http://localhost:5000/linkedin/redirect-facebook'
    URI_AUTH = 'https://www.facebook.com/v12.0/dialog/oauth'
    URI_API = 'https://graph.facebook.com/v12.0'
    account = None

    def authorize(self):
        token = create_CSRF_token()
        params = {
            'client_id': self.CLIENT_ID,
            'redirect_uri': self.REDIRECT_URI,
            'state': token,
            'scope': 'email'
        }
        response = requests.get(f'{self.URI_AUTH}', params=params)
        webbrowser.open(response.url)

    def get_id(self, auth_code):
        params = {
            'access_token': auth_code,
        }
        response = requests.get(f'{self.URI_API}' + f'/me', params=params)
        print(response.status_code)
        res = response.json()
        print("res", res)
        return res

    def refresh_user_token(self, auth_code):
        params = {
            'grant_type': 'fb_exchange_token',
            'fb_exchange_token': auth_code,
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET
        }

        response = requests.get('https://graph.facebook.com/oauth' + '/access_token', params=params, timeout=30)
        print(response.status_code)
        print(response.url)
        res = response.json()
        print(res)

    # def refresh_page_token(self, auth_code):
        # curl - i - X
        # GET
        # "https://graph.facebook.com/{graph-api-version}/{user-id}/accounts?
        # access_token = {long - lived - user - access - token}
        # "