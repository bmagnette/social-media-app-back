import json
import os
from functools import partial

import requests
from flask import Blueprint, request, redirect

from core.helpers.handlers import login_required
from core.libs.Social.Facebook import FacebookLogin
from core.libs.Social.Linkedin import LinkedInAPI
from core.libs.Social.Twitter import TwitterApi
from core.models.Social.account import MediaType
from core.models.user import User

oauth2_router = Blueprint('oauth2', __name__)


@oauth2_router.route("/redirect-linkedin", methods=["GET"])
def redirect_oauth():
    auth_code = request.args["code"]
    linkedin = LinkedInAPI()
    refreshed_token = linkedin.refresh_token(auth_code)
    linkedin_info = linkedin.user_info(refreshed_token)

    payload = {
        "social_type": MediaType.LINKEDIN.value,
        "social_id": linkedin_info["id"],
        "last_name": linkedin_info["localizedLastName"],
        "first_name": linkedin_info["localizedFirstName"],
        "profile_picture": linkedin_info["profilePicture"]["displayImage"],
        "expired_in": 60,
        "facebook_token": str(refreshed_token)
    }

    res = requests.post(os.environ["BACK_END_APP_URI"] + "/account",
                        data=json.dumps(payload),
                        headers={'Content-Type': 'application/json', 'Authorization': request.args["state"]})

    res.raise_for_status()
    return redirect(os.environ["FRONT_END_APP_URI"] + "/accounts")


@oauth2_router.route("/authorize", methods=["POST"])
@partial(login_required, payment_required=True)
def authorize(current_user: User):
    LinkedInAPI().authorize(current_user)
    return {}, 200


@oauth2_router.route("/redirect-facebook", methods=["GET"])
def redirect_oauth_facebook():
    auth_code = request.args["code"]
    state = request.args["state"]
    print(auth_code, state)
    FacebookLogin().refresh_user_token(auth_code)
    # _id = FacebookLogin().get_id(auth_code)

    # res = requests.post("http://localhost:5000/account",
    #                     data=json.dumps(
    #                         {"auth_code": str(auth_code), "expired_in": 500000,
    #                          "type": MediaType.FACEBOOK.value, "info": linkedin_info}),
    #                     headers={'Content-Type': 'application/json'})
    #
    # res.raise_for_status()

    # social_id = user_info["info"]["id"],
    # locale = user_info["info"]["lastName"]["preferredLocale"]["country"],
    # last_name = user_info["info"]["localizedLastName"],
    # first_name = user_info["info"]["localizedFirstName"],
    # profile_picture = user_info["info"]["profilePicture"]["displayImage"],
    # expired_in = user_info["expired_in"]
    return redirect("http://localhost:3000/accounts")


@oauth2_router.route("/facebook-authorize", methods=["POST"])
@partial(login_required, payment_required=True)
def authorize_facebook(current_user: User):
    FacebookLogin().authorize()
    return {}, 200


# @oauth2_router.route("/redirect-twitter", methods=["GET"])
# def redirect_oauth_twitter():
#     data = TwitterApi().callback(current_user.id, request.args.get('oauth_verifier'))
#
#     res = requests.post("http://localhost:5000/account",
#                         data=json.dumps(
#                             {"twitter_oauth_token": data["oauth_token"],
#                              "twitter_oauth_secret": data["oauth_token_secret"],
#                              "expired_in": None, "profile_picture": "",
#                              "social_id": data["user_id"],
#                              "account_name": data["screen_name"],
#                              "social_type": MediaType.TWITTER.value}),
#                         headers={'Content-Type': 'application/json'})
#
#     res.raise_for_status()
#     return redirect("http://localhost:3000")


@oauth2_router.route("/twitter-authorize", methods=["POST"])
@partial(login_required, payment_required=True)
def authorize_twitter(current_user: User):
    TwitterApi().authorize(current_user.id)
    return {}, 200
