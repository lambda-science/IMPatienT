from app.email import send_email
from flask import current_app, render_template


def send_password_reset_email(user):
    """Sent a token by email to reset the password

    Args:
        user (SQLAlchemy Object): The user who requested the password reset
    """
    token = user.get_reset_password_token()
    send_email(
        ("[IMPatienT] Reset Your Password"),
        sender=current_app.config["ADMINS_EMAIL"][0],
        recipients=[user.email],
        text_body=render_template("email_reset_password.txt", user=user, token=token),
        html_body=render_template("email_reset_password.html", user=user, token=token),
    )
