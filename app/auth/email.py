from flask import render_template, current_app
from app.email import send_email


def send_password_reset_email(user):
    """Function to send a token by email to user to reset his password"""
    token = user.get_reset_password_token()
    send_email(
        ("[EHRoes] Reset Your Password"),
        sender=current_app.config["ADMINS_EMAIL"][0],
        recipients=[user.email],
        text_body=render_template("email_reset_password.txt", user=user, token=token),
        html_body=render_template("email_reset_password.html", user=user, token=token),
    )
