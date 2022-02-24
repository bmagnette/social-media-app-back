import enum

from flask import current_app
from sqlalchemy import TIMESTAMP, func

from core.extensions import db


class MediaType(str, enum.Enum):
    FACEBOOK_PAGE = "FACEBOOK_PAGE"
    FACEBOOK_GROUP = "FACEBOOK_GROUP"
    FACEBOOK = "FACEBOOK"
    PINTEREST = "PINTEREST"
    LINKEDIN = "LINKEDIN"
    INSTAGRAM = "INSTAGRAM"
    TWITTER = "TWITTER"

    def __str__(self):
        return self.value


def initiate_account(user, **kwargs):
    account = Account(
        **kwargs
    )
    db.session.add(account)
    user.accounts.append(account)
    db.session.commit()
    current_app.logger.info(f'{user.id} - Adding new {account.social_type} account')
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

    social_type = db.Column(db.String, nullable=False)
    social_id = db.Column(db.String, nullable=False)

    name = db.Column(db.String(255), nullable=True)

    profile_picture = db.Column(db.Text())
    profile_img = db.Column(db.Text(10000000))

    created_at = db.Column(TIMESTAMP(True), server_default=func.now())

    access_token = db.Column(db.String, nullable=False)
    refresh_token = db.Column(db.String, nullable=True)

    expired_in = db.Column(db.Integer)

    def __init__(self, **kwargs):
        super(Account, self).__init__(**kwargs)
