import enum
from datetime import datetime

from core.extensions import db


class MediaType(str, enum.Enum):
    LINKEDIN = "LINKEDIN"
    INSTAGRAM = "INSTAGRAM"
    FACEBOOK = "FACEBOOK"
    TWITTER = "TWITTER"

    def __str__(self):
        print("jere")
        return self.value


def initiate_account(user, **kwargs):
    print(kwargs)
    account = Account(
        **kwargs
    )
    db.session.add(account)
    user.accounts.append(account)
    db.session.commit()
    return account


accounts = db.Table('accounts_join',
                    db.Column('account_id', db.Integer, db.ForeignKey('account.account_id'), primary_key=True),
                    db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
                    )


class Account(db.Model):
    __tablename__ = 'account'

    id = db.Column('account_id', db.Integer, primary_key=True)

    category_id = db.Column(db.Integer, db.ForeignKey('account_category.category_id'), nullable=True)
    category = db.relationship('AccountCategory', back_populates="accounts", single_parent=True)

    posts = db.relationship("Post", back_populates="account", cascade="all, delete-orphan")

    social_type = db.Column(db.Enum(MediaType), nullable=False)
    social_id = db.Column(db.String, nullable=False)

    locale = db.Column(db.String, nullable=True)

    last_name = db.Column(db.String, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    account_name = db.Column(db.String, nullable=True)

    profile_picture = db.Column(db.Text())

    created_at = db.Column(db.Float, default=datetime.utcnow().timestamp())

    facebook_token = db.Column(db.String, nullable=True)

    twitter_oauth_token = db.Column(db.String, nullable=True)
    twitter_oauth_secret = db.Column(db.String, nullable=True)

    expired_in = db.Column(db.Integer)

    def __init__(self, **kwargs):
        super(Account, self).__init__(**kwargs)
