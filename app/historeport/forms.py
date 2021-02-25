from app.models import Patient, Image
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, Length
import os

class ReportForm(FlaskForm):
    """Form used for report registration."""
    #submit = SubmitField('Submit report to the database',
    #                     render_kw={"class": "btn btn-primary mb-2"})
