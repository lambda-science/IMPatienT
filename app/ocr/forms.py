import os
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired
import app.src.common as Common


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

    lang = SelectField(
        "lang",
        validators=[DataRequired()],
        choices=Common.create_lang_list(os.path.join("config", "config_lang_ocr.tsv")),
        render_kw={"placeholder": "PDF Langage", "class": "form-control custom-select"},
    )
    submit = SubmitField("Upload", render_kw={"class": "btn btn-primary mb-2"})


class DeleteButton(FlaskForm):
    """Empty form for delete button"""

    submit = SubmitField("Confirm Deletion", render_kw={"class": "btn btn-danger"})