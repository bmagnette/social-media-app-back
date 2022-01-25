from core.libs.Social.Linkedin import LinkedInAPI
from core.libs.Social.Twitter import TwitterApi
from core.models.account import Account


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
        acc = Account.query.filter_by(id=account_info["id"]).first()
        linkedin = LinkedInAPI()
        linkedin.account = acc
        return linkedin.write_post(account_info["token"], linkedin_payload)
    if account_info["social_type"] == "TWITTER":
        acc = Account.query.filter_by(id=account_info["id"]).first()
        twitter = TwitterApi()
        res = twitter.post(acc.twitter_oauth_token, acc.twitter_oauth_secret, message)
        return res
