import os
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired
import app.src.common as Common
from app.models import Patient


class PdfForm(FlaskForm):
    """Form used for handling of PDF upload associated to patient"""

    pdf = FileField(
        validators=[
            FileRequired(),
            FileAllowed(["pdf"], "This file is not a valid PDF File !"),
        ],
        render_kw={"class": "form-control-file border"},
    )
    patient_ID = StringField(
        "patient_ID",
        validators=[DataRequired()],
        render_kw={"placeholder": "Patient ID", "class": "form-control"},
    )
    patient_nom = StringField(
        "patient_nom",
        validators=[DataRequired()],
        render_kw={"placeholder": "Patient Last Name", "class": "form-control"},
    )
    patient_prenom = StringField(
        "patient_prenom",
        validators=[DataRequired()],
        render_kw={"placeholder": "Patient First Name", "class": "form-control"},
    )

    lang = SelectField(
        "lang",
        validators=[DataRequired()],
        choices=Common.create_lang_list(os.path.join("config", "config_lang_ocr.tsv")),
        render_kw={"placeholder": "PDF Langage", "class": "form-control custom-select"},
    )
    submit = SubmitField("Upload", render_kw={"class": "btn btn-primary mb-2"})

    def validate_patient_nom(self, patient_nom):
        """Check if patient ID correspond to given lastname"""
        patient = Patient.query.get(self.patient_ID.data)
        if patient is not None:
            if patient.patient_name != patient_nom.data:
                raise ValidationError(
                    str(
                        "Same Patient ID with different last name already exists: "
                        + patient.patient_name
                        + " ; Please use another ID or correct patient name"
                    )
                )

    def validate_patient_prenom(self, patient_prenom):
        """Check if patient ID correspond to given firstname"""
        patient = Patient.query.get(self.patient_ID.data)
        if patient is not None:
            if patient.patient_firstname != patient_prenom.data:
                raise ValidationError(
                    str(
                        "Same Patient ID with different firstname already exists: "
                        + patient.patient_firstname
                        + " ;  Please use another ID or correct patient name"
                    )
                )


class OcrForm(FlaskForm):
    """Form to save OCR results to database"""

    ocr_text = TextAreaField(
        render_kw={
            "rows": "25",
            "class": "form-control",
        }
    )
    submit = SubmitField(
        "Submit text to database and\n return to upload page",
        render_kw={"class": "btn btn-primary mb-2"},
    )


class DeleteButton(FlaskForm):
    """Empty form for delete button"""

    submit = SubmitField("Delete", render_kw={"class": "btn btn-danger"})
