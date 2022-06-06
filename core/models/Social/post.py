from sqlalchemy import TIMESTAMP, func

from core.extensions import db


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column('id', db.Integer, primary_key=True)

    event_id = db.Column(db.Integer, db.ForeignKey('calendar_event.calendar_event_id'), nullable=False)
    event = db.relationship('CalendarEvent', back_populates="posts")

    account_id = db.Column(db.Integer, db.ForeignKey('account.account_id'), nullable=False)
    account = db.relationship('Account', back_populates="posts")

    social_id = db.Column(db.String, nullable=True)

    type = db.Column(db.String, nullable=False)

    message = db.Column(db.String, nullable=False)
    photo = db.Column(db.Text(), nullable=True)

    created_at = db.Column(TIMESTAMP(True), server_default=func.now())
    updated_at = db.Column(TIMESTAMP(True), server_default=func.now())
