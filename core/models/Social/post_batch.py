from sqlalchemy import TIMESTAMP, func

from core.extensions import db


class PostBatch(db.Model):
    __tablename__ = 'post_batch'

    id = db.Column('batch_id', db.Integer, primary_key=True)

    author_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    author = db.relationship('User', back_populates="posted")

    posts = db.relationship("Post", back_populates="batch")

    created_at = db.Column(TIMESTAMP(True), server_default=func.now())
    updated_at = db.Column(TIMESTAMP(True), server_default=func.now())
    schedule_date = db.Column(TIMESTAMP(True), nullable=True)

    isScheduled = db.Column(db.Boolean, default=False)
