from threading import Thread

from flask import current_app
from flask_mail import Message

from app import mail


def send_async_email(app, msg):
    """Send email asynchronously

    Args:
        app (Flask Application Object): Our flask application object.
        msg (str): the email content
    """
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    """Function to send mail using a thread (async).

    Args:
        subject (str): Mail Subject
        sender (str): Mail Sender
        recipients (list): Mail Recipients
        text_body (str): Mail Text Body
        html_body (str): Mail HTML Body
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(
        target=send_async_email, args=(current_app._get_current_object(), msg)
    ).start()
