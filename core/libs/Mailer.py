from threading import Thread

from flask import current_app
from flask_mail import Message

from core.extensions import mail


def send_email(subject, sender, recipients, html_body):
    """
    Global function to send email.
    :param subject:
    :param sender:
    :param recipients:
    :param html_body:
    :return:
    """

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    # attach_pictures(msg)

    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
