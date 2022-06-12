from sqlalchemy import TIMESTAMP, func
from enum import Enum

from core.extensions import db
from core.models.Social.account import MediaType


class PostStatus(Enum):
    IN_WRITING = "IN_WRITING"
    WAITING_FOR_VALIDATION = "WAITING_FOR_VALIDATION"
    PROCESSING = "PROCESSING"
    SCHEDULED = "SCHEDULED"
    POSTED = "POSTED"
    POSTING_ERROR = "POSTING_ERROR"


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column('id', db.Integer, primary_key=True)

    event_id = db.Column(db.Integer, db.ForeignKey('calendar_event.calendar_event_id'), nullable=False)
    event = db.relationship('CalendarEvent', back_populates="posts")

    account_id = db.Column(db.Integer, db.ForeignKey('account.account_id'), nullable=False)
    account = db.relationship('Account', back_populates="posts")

    social_id = db.Column(db.String, nullable=True)

    type = db.Column(db.Enum(MediaType), nullable=False)
    status = db.Column(db.Enum(PostStatus), nullable=False)

    message = db.Column(db.String, nullable=False)

    media_b64 = db.Column(db.ARRAY(db.Text()), nullable=True)
    media_link = db.Column(db.ARRAY(db.Text()), nullable=True)

    created_at = db.Column(TIMESTAMP(True), server_default=func.now())
    updated_at = db.Column(TIMESTAMP(True), server_default=func.now())
