from core.libs.Social.Twitter import TwitterApi
from core.libs.Oauth2.oauth import LinkedInSignIn, FacebookSignIn
from core.models.Social.account import Account


def send_message(user_id, account_info: dict, message: str):
    if account_info["social_type"] == 'LINKEDIN':
        linkedin_payload = {
            "author": '',
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": ''
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        linkedin_payload["author"] = f'urn:li:person:{account_info["social_id"]}'
        linkedin_payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareCommentary"][
            "text"] = message
        return LinkedInSignIn().post(account_info["facebook_token"], linkedin_payload)
    if account_info["social_type"] == "TWITTER":
        acc = Account.query.filter_by(id=account_info["id"]).first()
        twitter = TwitterApi()
        res = twitter.post(acc.twitter_oauth_token, acc.twitter_oauth_secret, message)
        return res
    if account_info["social_type"] == "FACEBOOK":
        acc = Account.query.filter_by(id=account_info["id"]).first()

        res = FacebookSignIn().post(acc.social_id, acc.facebook_token)
        return res
