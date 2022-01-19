from datetime import datetime

from core.extensions import db


class PostBatch(db.Model):
    __tablename__ = 'post_batch'

    id = db.Column('batch_id', db.Integer, primary_key=True)

    author_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    author = db.relationship('User', back_populates="posted")

    posts = db.relationship("Post", back_populates="batch")

    created_at = db.Column(db.Float, default=datetime.utcnow().timestamp())
    updated_at = db.Column(db.Float, default=datetime.utcnow().timestamp())

    isScheduled = db.Column(db.Boolean, default=False)
    schedule_date = db.Column(db.Float, nullable=True)
    schedule_hour = db.Column(db.Float, nullable=True)
    schedule_minute = db.Column(db.Float, nullable=True)


