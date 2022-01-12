import enum
from datetime import datetime

from core.extensions import db


class MediaType(str, enum.Enum):
    LINKEDIN = "LINKEDIN"
    INSTAGRAM = "INSTAGRAM"
    FACEBOOK = "FACEBOOK"
    TWITTER = "TWITTER"


def initiate_account(user, user_info):
    account = Account(
        social_type=user_info["type"],
        social_id=user_info["info"]["id"],
        locale=user_info["info"]["lastName"]["preferredLocale"]["country"],
        last_name=user_info["info"]["localizedLastName"],
        first_name=user_info["info"]["localizedFirstName"],
        profile_picture=user_info["info"]["profilePicture"]["displayImage"],
        token=user_info["auth_code"],
        expired_in=user_info["expired_in"]
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

    locale = db.Column(db.String, nullable=False)

    last_name = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    profile_picture = db.Column(db.Text())

    created_at = db.Column(db.Float, default=datetime.utcnow().timestamp())

    token = db.Column(db.String, nullable=False)
    expired_in = db.Column(db.Float)

    def __init__(self, **kwargs):
        super(Account, self).__init__(**kwargs)
