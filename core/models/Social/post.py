from datetime import datetime

from core.extensions import db
from core.models.Social.account import MediaType


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column('id', db.Integer, primary_key=True)

    batch_id = db.Column(db.Integer, db.ForeignKey('post_batch.batch_id'), nullable=False)
    batch = db.relationship('PostBatch', back_populates="posts")

    account_id = db.Column(db.Integer, db.ForeignKey('account.account_id'), nullable=False)
    account = db.relationship('Account', back_populates="posts")

    type = db.Column(db.Enum(MediaType), nullable=False)

    message = db.Column(db.String, nullable=False)
    photo = db.Column(db.Text(), nullable=True)

    created_at = db.Column(db.Float, default=datetime.utcnow().timestamp())
    updated_at = db.Column(db.Float, default=datetime.utcnow().timestamp())
