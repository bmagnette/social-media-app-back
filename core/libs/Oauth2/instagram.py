from core.libs.Oauth2.oauth import OAuthSignIn


class InstagramSignIn(OAuthSignIn):
    def __init__(self):
        super(InstagramSignIn, self).__init__('instagram')
