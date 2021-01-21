from app.models import Patient, Image
#from flask import current_app
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, Length

import app.src.common as Common
import os


class ImageForm(FlaskForm):
    image = FileField(
        validators=[
            FileRequired(),
            #FileAllowed(current_app.config["ALLOWED_EXTENSIONS"],
            #            "This file is not a valid image !")
            FileAllowed(["tif", "tiff", "png", "jpg", "jpeg"],
                        "This file is not a valid image !")
        ],
        render_kw={"class": "form-control-file"})
    patient_ID = StringField('patient_ID',
                             validators=[DataRequired()],
                             render_kw={
                                 "placeholder": "Patient ID",
                                 "class": "form-control"
                             })
    patient_nom = StringField('patient_nom',
                              validators=[DataRequired()],
                              render_kw={
                                  "placeholder": "Patient Last Name",
                                  "class": "form-control"
                              })
    patient_prenom = StringField('patient_prenom',
                                 validators=[DataRequired()],
                                 render_kw={
                                     "placeholder": "Patient First Name",
                                     "class": "form-control"
                                 })
    submit = SubmitField('Upload', render_kw={"class": "btn btn-primary mb-2"})

    def validate_patient_nom(self, patient_nom):
        patient = Patient.query.get(self.patient_ID.data)
        if patient is not None:
            if patient.patient_name != patient_nom.data:
                raise ValidationError(
                    str('Same Patient ID with different last name already exists: '
                        + patient.patient_name +
                        " ; Please use another ID or correct patient name"))

    def validate_patient_prenom(self, patient_prenom):
        patient = Patient.query.get(self.patient_ID.data)
        if patient is not None:
            if patient.patient_firstname != patient_prenom.data:
                raise ValidationError(
                    str('Same Patient ID with different firstname already exists: '
                        + patient.patient_firstname +
                        " ;  Please use another ID or correct patient name"))


class AnnotForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(AnnotForm, self).__init__(*args, **kwargs)

    submit = SubmitField('Submit report and annotations to the database',
                         render_kw={"class": "btn btn-primary mb-2"})

    diagnostic = SelectField(
        'diagnostic',
        validators=[DataRequired()],
        #choices=current_app.config["DIAG_LIST"],
        choices=Common.create_diag_list(
            os.path.join("config", "diagnostic.tsv")),
        render_kw={
            "placeholder": "Disease diagnostic",
            "class": "form-control custom-select"
        })


#for feature in current_app.config["FEATURE_LIST"]:
for feature in Common.create_feature_list(
        os.path.join("config", "config_ontology.tsv")):
    setattr(
        AnnotForm, feature[0],
        RadioField(feature[1],
                   choices=[('1', 'Present'), ('-1', 'Absent'),
                            ('0', 'Uncertain')],
                   default='-1',
                   validators=[DataRequired()]))