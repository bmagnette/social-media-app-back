import enum
import random
import string
from datetime import datetime, timedelta

from sqlalchemy import ForeignKey, TIMESTAMP, func
from werkzeug.security import check_password_hash

from core.extensions import db
from core.models.Social.account import accounts
from core.models.Social.account_category import categories


class UserRight(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    READER = "READER"


class UserType(enum.Enum):
    CORPORATE = "CORPORATE"
    PRIVATE = "PRIVATE"


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column('user_id', db.Integer, primary_key=True)

    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    is_confirmed = db.Column(db.Boolean, default=True)

    # User Info
    right = db.Column(db.Enum(UserRight), nullable=False, default=UserRight.ADMIN)
    profile = db.Column(db.String(255), nullable=False)

    organization = db.Column(db.String(255), nullable=True)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)

    # Date
    created_at = db.Column(TIMESTAMP(True), server_default=func.now())
    updated_at = db.Column(TIMESTAMP(True), server_default=func.now())
    last_login = db.Column(TIMESTAMP(True), default=None)

    # Many to many relationship
    accounts = db.relationship('Account', secondary=accounts, lazy='dynamic',
                               backref=db.backref('user', lazy=True))
    categories = db.relationship('AccountCategory', secondary=categories, lazy='dynamic',
                                 backref=db.backref('user', lazy=True))

    # One to Many
    posted = db.relationship("PostBatch", back_populates="author")
    invoices = db.relationship("Invoice", back_populates="user")

    sponsor_id = db.Column(db.String(15),
                           default=''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10)))

    # One to One
    customer_id = db.Column(db.Integer, ForeignKey('stripe_customer.customer_id'), nullable=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_accounts(self):
        return len(self.accounts.all())

    def get_price(self):
        nb_accounts = self.get_accounts()
        if nb_accounts <= 2:
            return 0
        elif 3 <= nb_accounts <= 5:
            return 20
        elif 6 <= nb_accounts <= 10:
            return 30
        elif 11 <= nb_accounts <= 30:
            return 50
        elif 31 <= nb_accounts <= 100:
            return 125
        elif 101 <= nb_accounts <= 10000:
            return 500
        else:
            raise Exception("Pricing not defined")

    def get_end_free_trial(self):
        return self.created_at + timedelta(days=14)
