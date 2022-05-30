import enum

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import backref

from core.extensions import db
from core.models.Social.account import Account
from core.models.user import User


class AccessType(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    READER = "READER"



# categories = db.Table('category_join',
#                       db.Column('category_id', db.Integer, db.ForeignKey('account_category.category_id'),
#                                 primary_key=True),
#                       db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), primary_key=True),
#                       db.Column('access_type', db.Enum(AccessType), nullable=False, default=AccessType.ADMIN)
#                       )


# class CategoryUserAssociation(db.Model):
#     __tablename__ = 'category_user_association'
#     category_id = db.Column('category_id', db.ForeignKey('account_category.category_id'), primary_key=True)
#     user_id = db.Column('user_id', db.ForeignKey('user.user_id'), primary_key=True)
#
#     access_type = db.Column(db.Enum(AccessType), nullable=False, default=AccessType.ADMIN)
#
#     category = db.relationship("AccountCategory", back_populates="users")
#     user = db.relationship("User", back_populates="asso_categories")


def initiate_account_category(current_user, data):
    # a = CategoryUserAssociation()

    category = AccountCategory(
        label=data["categoryName"],
        color=data["color"],
        logo="",
    )
    db.session.add(category)
    db.session.commit()
    for account in data["accounts"]:
        account = Account.query.filter_by(id=account["id"]).first_or_404()
        category.accounts.append(account)

    category.access_type = "test"
    current_user.categories.append(category)
    db.session.commit()
    return category


class AccountCategory(db.Model):
    __tablename__ = 'account_category'

    id = db.Column('category_id', db.Integer, primary_key=True)

    label = db.Column(db.String, nullable=False)
    color = db.Column(db.String, nullable=False)

    logo = db.Column(db.Text(), nullable=True)

    created_at = db.Column(TIMESTAMP(True), server_default=func.now())
    updated_at = db.Column(TIMESTAMP(True), server_default=func.now())

    accounts = db.relationship("Account", uselist=True, back_populates="category")
    users = db.relationship("User", secondary='join_category_group')


class CategoryGroup(db.Model):
    __tablename__ = 'join_category_group'
    category_id = db.Column(db.Integer, db.ForeignKey('account_category.category_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)

    access_type = db.Column(db.Enum(AccessType), nullable=False, default=AccessType.ADMIN)

    category = db.relationship(AccountCategory, backref=backref("category_assoc"))
    user = db.relationship(User, backref=backref("user_assoc", cascade="save-update, merge, "
                                                "delete, delete-orphan"))
