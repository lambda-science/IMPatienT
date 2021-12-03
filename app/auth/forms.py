from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo


class LoginForm(FlaskForm):
    """Login

    Args:
        FlaskForm (FlaskForm Class): The FlaskForm Class
    """

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
        ],
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class ResetPasswordRequestForm(FlaskForm):
    """Reset Password Request Form

    Args:
        FlaskForm (FlaskForm Class): The FlaskForm Class
    """

    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    """New password form

    Args:
        FlaskForm (FlaskForm Class): The FlaskForm Class
    """

    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Request Password Reset")


# class RegistrationForm(FlaskForm):
#    """The form used for registration"""
#    username = StringField('Username',
#                           validators=[
#                               DataRequired(),
#                               Regexp(r'^[\w.@+-]+$'),
#                               Length(min=4, max=25)
#                           ])
#    email = StringField('Email', validators=[DataRequired(), Email()])
#    password = PasswordField('Password', validators=[DataRequired()])
#    password2 = PasswordField('Repeat Password',
#                              validators=[DataRequired(),
#                                          EqualTo('password')])
#    submit = SubmitField('Register')
#
#    def validate_username(self, username):
#        """Function used to check if username already exist"""
#        user = User.query.filter_by(username=username.data).first()
#       if user is not None:
#            raise ValidationError('Username already exists.')
#
#    def validate_email(self, email):
#        """Function used to check if email already exist"""
#        user = User.query.filter_by(email=email.data).first()
#        if user is not None:
#            raise ValidationError('Email already used.')
