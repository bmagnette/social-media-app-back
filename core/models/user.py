import enum
import random
import string
from datetime import datetime

from core.extensions import db
from core.models.account import accounts
from core.models.account_category import categories


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

    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String)

    # User Info
    right = db.Column(db.Enum(UserRight), nullable=False, default=UserRight.ADMIN)
    profile = db.Column(db.String, nullable=False)

    organization = db.Column(db.String, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)

    # Date
    created_at = db.Column(db.Float, default=datetime.utcnow().timestamp())
    updated_at = db.Column(db.Float, default=datetime.utcnow().timestamp())
    last_login = db.Column(db.Float, default=None)

    # Many to many relationship
    accounts = db.relationship('Account', secondary=accounts, lazy='dynamic',
                               backref=db.backref('user', lazy=True))
    categories = db.relationship('AccountCategory', secondary=categories, lazy='dynamic',
                                 backref=db.backref('user', lazy=True))

    # One to Many
    posted = db.relationship("PostBatch", back_populates="author")

    sponsor_id = db.Column(db.String, nullable=False,
                           default=''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10)))

    stripe_id = db.Column(db.String, nullable=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
