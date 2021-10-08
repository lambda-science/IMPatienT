import os
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Regexp
import app.src.common as Common


class ImageForm(FlaskForm):
    """Form used for image uploading"""

    image = FileField(
        validators=[
            FileRequired(),
            FileAllowed(["png", "jpg", "jpeg"], "This file is not a valid image !",),
        ],
        render_kw={"class": "form-control-file border"},
    )
    patient_ID = StringField(
        "patient_ID",
        validators=[Regexp(r"^[\w.-_]+$"), DataRequired()],
        render_kw={"placeholder": "Patient ID", "class": "form-control"},
    )
    biopsy_report_ID = StringField(
        "biopsy_report_ID",
        validators=[DataRequired(), Regexp(r"^[\w.-_]*$")],
        render_kw={"placeholder": "Biopsy Report ID", "class": "form-control"},
    )
    type_coloration = SelectField(
        "type_coloration",
        validators=[DataRequired()],
        choices=[
            "HE",
            "TG",
            "ATP",
            "NADH/SDH",
            "COX",
            "PAS",
            "Sudan Lipids",
            "Phosphorylases",
            "ME",
        ],
        render_kw={
            "placeholder": "Histology Coloration Type",
            "class": "form-control custom-select",
        },
    )
    age_histo = SelectField(
        "age_histology",
        validators=[DataRequired()],
        choices=[i for i in range(131)],
        render_kw={
            "placeholder": "Patient age at histology sample time",
            "class": "form-control custom-select",
        },
    )
    diagnostic = SelectField(
        "diagnostic",
        validators=[DataRequired()],
        choices=Common.create_diag_list(os.path.join("config", "diagnostic.tsv")),
        render_kw={
            "placeholder": "Disease diagnostic",
            "class": "form-control custom-select",
        },
    )

    submit = SubmitField("Upload", render_kw={"class": "btn btn-primary mb-2"})


class DeleteButton(FlaskForm):
    """Empty form for delete button"""

    submit = SubmitField("Confirm Deletion", render_kw={"class": "btn btn-danger"})