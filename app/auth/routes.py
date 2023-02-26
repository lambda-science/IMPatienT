from app import db, login_manager
from app.auth import bp
from app.auth.email import send_password_reset_email
from app.auth.forms import LoginForm, ResetPasswordForm, ResetPasswordRequestForm
from app.models import User
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse


@login_manager.unauthorized_handler
def handle_needs_login():
    flash("You have to be logged in to access this page.", "info")
    return redirect(url_for("auth.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    """The login page

    Returns:
        str: Login HTML Page
    """
    # Already auth. user are redirected to index
    if current_user.is_authenticated:
        return redirect(url_for("index.index"))
    form = LoginForm()
    if form.validate_on_submit():
        # Check if password match
        user = User.objects(username=form.username.data).first()
        if not user or not user.check_password(form.password.data):
            flash("Invalid username or password", "danger")
            return redirect(url_for("auth.login"))
        # Log user if password matched, store username and redirect user
        login_user(user, remember=form.remember_me.data)
        flash("Login successful", "success")
        return redirect(url_for("index.index"))
    return render_template("login.html", title="Sign In", form=form)


@bp.route("/logout")
def logout():
    """Logout Page

    Returns:
        str: Logout HTML Page
    """ """View page to logout"""
    flash("You were logged out", "info")
    logout_user()
    return redirect(url_for("auth.login"))


@bp.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    """Reset password request page

    Returns:
        str: Reset password request HTML Page or redirection to login page
    """ """View page to request password reset"""
    # If Logged already: redirect to index
    if current_user.is_authenticated:
        return redirect(url_for("index.index"))
    form = ResetPasswordRequestForm()
    # If form validated, look for user in database and create the token & email for password reset
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash(
                "Check your email for the instructions to reset your password",
                "success",
            )
        else:
            flash("No account found for this email.", "danger")
        return redirect(url_for("auth.login"))
    return render_template(
        "reset_password_request.html", title="Reset Password", form=form
    )


@bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Create new password page

    Args:
        token (str): JWT-Token to reset password

    Returns:
        str: HTML Page to create new password or redirection to login page
    """
    # If Logged already: redirect to index
    if current_user.is_authenticated:
        return redirect(url_for("index.index"))
    # Filter user by verifying token. Redirect if not valid. Else new password form
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("index.index"))
    form = ResetPasswordForm()
    # Save new password to DB
    if form.validate_on_submit():
        my_user = user
        my_user.set_password(form.password.data)
        my_user.save()
        flash("Your password has been reset.")
        return redirect(url_for("auth.login"))
    return render_template("reset_password.html", form=form)


# @bp.route('/register', methods=['GET', 'POST'])
# def register():
#    """View page to register"""
#    # Redirect if already logged
#    if current_user.is_authenticated:
#        return redirect(url_for('index.index'))
#    form = RegistrationForm()
#    # If form validated, register user to database
#    if form.validate_on_submit():
#        user = User(username=form.username.data, email=form.email.data)
#        user.set_password(form.password.data)
#        db.session.add(user)
#        db.session.commit()
#        flash('Congratulations, you are now a registered user!', "success")
#        return redirect(url_for('auth.login'))
#    return render_template('register.html', title='Register', form=form)
