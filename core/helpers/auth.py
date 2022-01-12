import random
import string


def create_CSRF_token():
    """
    This function generates a random string of letters.
    It is not required by the Linkedin API to use a CSRF token.
    However, it is recommended to protect against cross-site request forgery
    """
    letters = string.ascii_lowercase
    token = ''.join(random.choice(letters) for i in range(20))
    return token


def headers_bearer(access_token):
    """
    Make the headers to attach to the API call.
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'cache-control': 'no-cache',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    return headers


def header():
    return {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }
