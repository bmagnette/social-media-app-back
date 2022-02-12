from sqlalchemy import TIMESTAMP, func

from core.extensions import db
from core.models.Social.account import Account

categories = db.Table('category_join',
                      db.Column('category_id', db.Integer, db.ForeignKey('account_category.category_id'),
                                primary_key=True),
                      db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
                      )


def initiate_account_category(current_user, data):
    category = AccountCategory(
        label=data["categoryName"],
        description=data["categoryDescription"],
        logo="",
    )
    db.session.add(category)
    db.session.commit()
    for account in data["accounts"]:
        account = Account.query.filter_by(id=account["id"]).first_or_404()
        category.accounts.append(account)

    current_user.categories.append(category)
    db.session.commit()
    return category


class AccountCategory(db.Model):
    __tablename__ = 'account_category'

    id = db.Column('category_id', db.Integer, primary_key=True)

    label = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    accounts = db.relationship("Account", uselist=True, back_populates="category")

    logo = db.Column(db.Text(), nullable=True)
    created_at = db.Column(TIMESTAMP(True), server_default=func.now())
    updated_at = db.Column(TIMESTAMP(True), server_default=func.now())
