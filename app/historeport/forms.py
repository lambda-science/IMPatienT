from app.models import Patient, Image
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, SelectField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, Length
import os
from datetime import datetime


class ReportForm(FlaskForm):
    """Form used for report registration."""
    patient_nom = StringField('patient_nom',
                              render_kw={
                                  "placeholder": "Nom Patient",
                                  "class": "form-control"
                              })
    patient_prenom = StringField('patient_prenom',
                                 render_kw={
                                     "placeholder": "Prénom Patient",
                                     "class": "form-control"
                                 })
    naissance = StringField(
        'naissance',
        validators=[
            Regexp(
                r'(^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$)|(^$)'
            ),
            Length(max=10)
        ],
        render_kw={
            "placeholder": "Date de naissance YYYY-MM-DD",
            "class": "form-control"
        })
    biopsie_ID = StringField('biopsie_ID',
                             render_kw={
                                 "placeholder": "Numéro de Biopsie",
                                 "class": "form-control"
                             })
    muscle_prelev = StringField('muscle_prelev',
                                render_kw={
                                    "placeholder": "Muscle biopsie",
                                    "class": "form-control"
                                })
    age_biopsie = SelectField('Age du patient lors de la biopsie:',
                              choices=["N/A"] + [i for i in range(101)],
                              default="N/A",
                              render_kw={
                                  "placeholder":
                                  "Age du patient lors de la biopsie",
                                  "class": "form-control custom-select"
                              })
    date_envoie = StringField(
        'date_envoie',
        validators=[
            Regexp(
                r'(^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$)|(^$)'
            ),
            Length(max=10)
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "Date d'envoie rapport YYYY-MM-DD",
        })
