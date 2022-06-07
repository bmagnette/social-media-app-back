import enum

from sqlalchemy import TIMESTAMP, func

from core.extensions import db


class EventType(enum.Enum):
    DEFAULT = "DEFAULT"
    POST = "POST"
    CUSTOM = "CUSTOM"


class CalendarEvent(db.Model):
    __tablename__ = 'calendar_event'

    id = db.Column('calendar_event_id', db.Integer, primary_key=True)

    author_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    author = db.relationship('User', back_populates="events")

    posts = db.relationship("Post", back_populates="event")

    event_type = db.Column(db.Enum(EventType), nullable=False)

    created_at = db.Column(TIMESTAMP(True), server_default=func.now())
    updated_at = db.Column(TIMESTAMP(True), server_default=func.now())

    event_date = db.Column(TIMESTAMP(True), nullable=True)

    title = db.Column(db.String, nullable=True, default=None)

    schedule_date = db.Column(TIMESTAMP(True), nullable=True)

    isScheduled = db.Column(db.Boolean, default=False)
    is_all_day = db.Column(db.Boolean, default=False)
