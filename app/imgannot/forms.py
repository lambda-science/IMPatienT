import os
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired
from app.models import Patient
import app.src.common as Common


class ImageForm(FlaskForm):
    """Form used for image uploading"""
    image = FileField(validators=[
        FileRequired(),
        FileAllowed([
            "tif", "tiff", "png", "jpg", "jpeg", "svs", "vms", "vmu", "ndpi",
            "scn", "mrxs", "bif", "svslide"
        ], "This file is not a valid image !")
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
        """Check if patient lastname correspond to already in DB patient_ID"""
        patient = Patient.query.get(self.patient_ID.data)
        if patient is not None:
            if patient.patient_name != patient_nom.data:
                raise ValidationError(
                    str('Same Patient ID with different last name already exists: '
                        + patient.patient_name +
                        " ; Please use another ID or correct patient name"))

    def validate_patient_prenom(self, patient_prenom):
        """Check if patient firstname correspond to already in DB patient_ID"""
        patient = Patient.query.get(self.patient_ID.data)
        if patient is not None:
            if patient.patient_firstname != patient_prenom.data:
                raise ValidationError(
                    str('Same Patient ID with different firstname already exists: '
                        + patient.patient_firstname +
                        " ;  Please use another ID or correct patient name"))


class AnnotForm(FlaskForm):
    """Form used for image global annotation. Feature list are added later"""
    def __init__(self, *args, **kwargs):
        super(AnnotForm, self).__init__(*args, **kwargs)

    submit = SubmitField('Submit report and annotations to the database',
                         render_kw={"class": "btn btn-primary mb-2"})
    type_coloration = SelectField('type_coloration',
                                  validators=[DataRequired()],
                                  choices=Common.create_list(
                                      os.path.join("config",
                                                   "config_coloration.txt")),
                                  render_kw={
                                      "placeholder":
                                      "Histology Coloration Type",
                                      "class": "form-control custom-select"
                                  })
    age_histo = SelectField('age_histology',
                            validators=[DataRequired()],
                            choices=[i for i in range(131)],
                            render_kw={
                                "placeholder":
                                "Patient age at histology sample time",
                                "class": "form-control custom-select"
                            })
    diagnostic = SelectField('diagnostic',
                             validators=[DataRequired()],
                             choices=Common.create_diag_list(
                                 os.path.join("config", "diagnostic.tsv")),
                             render_kw={
                                 "placeholder": "Disease diagnostic",
                                 "class": "form-control custom-select"
                             })
