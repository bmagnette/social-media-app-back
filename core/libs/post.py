from core.libs.Linkedin import LinkedInAPI
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
