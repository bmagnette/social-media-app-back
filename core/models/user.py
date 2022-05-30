import enum
import random
import string
from datetime import timedelta

from sqlalchemy import ForeignKey, TIMESTAMP, func
from werkzeug.security import check_password_hash

from core.extensions import db
from core.models.Social.account import accounts, Account


class UserType(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column('user_id', db.Integer, primary_key=True)
    admin_id = db.Column('admin_id', db.Integer, default=None)

    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    is_confirmed = db.Column(db.Boolean, default=True)

    # User Info
    user_type = db.Column(db.Enum(UserType), nullable=False, default=UserType.ADMIN)

    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)

    # Date
    created_at = db.Column(TIMESTAMP(True), server_default=func.now())
    updated_at = db.Column(TIMESTAMP(True), server_default=func.now())
    last_login = db.Column(TIMESTAMP(True), default=None)

    # Many to many relationship
    accounts = db.relationship('Account', secondary=accounts, lazy='dynamic',
                               backref=db.backref('user', lazy=True))

    # asso_categories = db.relationship("CategoryUserAssociation", back_populates="user")
    categories = db.relationship("AccountCategory", secondary='join_category_group')

    # categories = db.relationship('CategoryGroup')

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
        admin_id = self.id if self.user_type == UserType.ADMIN else self.admin_id
        admin = User.query.filter_by(id=admin_id).first_or_404()
        users = User.query.filter_by(admin_id=admin_id).all()
        i = len(admin.accounts.all())
        for user in users:
            i = i + len(user.accounts.all())
        return i

    def get_users(self):
        return len(User.query.filter_by(admin_id=self.id).all())

    def get_price(self):
        nb_accounts = self.get_accounts()
        user_pricing = self.get_users() * 5
        if nb_accounts <= 2:
            return 0
        elif 3 <= nb_accounts <= 5:
            return 20 + user_pricing
        elif 6 <= nb_accounts <= 10:
            return 30 + user_pricing
        elif 11 <= nb_accounts <= 30:
            return 50 + user_pricing
        elif 31 <= nb_accounts <= 100:
            return 125 + user_pricing
        elif 101 <= nb_accounts <= 10000:
            return 500 + user_pricing
        else:
            raise Exception("Pricing not defined")

    def get_end_free_trial(self):
        return self.created_at + timedelta(days=14)

    def is_admin(self):
        return self.user_type == UserType.ADMIN
