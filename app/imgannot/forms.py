import os
import json
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, SelectField, fields
from wtforms.validators import ValidationError, DataRequired
import app.src.common as Common


class JSONField(fields.StringField):
    """Form Field for JSON Handeling"""

    def _value(self):
        return json.dumps(self.data) if self.data else ""

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = json.loads(valuelist[0])
            except ValueError:
                raise ValueError("This field contains invalid JSON")
        else:
            self.data = None

    def pre_validate(self, form):
        super().pre_validate(form)
        if self.data:
            try:
                json.dumps(self.data)
            except TypeError:
                raise ValueError("This field contains invalid JSON")


class ImageForm(FlaskForm):
    """Form used for image uploading"""

    image = FileField(
        validators=[
            FileRequired(),
            FileAllowed(
                [
                    "tif",
                    "tiff",
                    "png",
                    "jpg",
                    "jpeg",
                    "svs",
                    "vms",
                    "vmu",
                    "ndpi",
                    "scn",
                    "mrxs",
                    "bif",
                    "svslide",
                ],
                "This file is not a valid image !",
            ),
        ],
        render_kw={"class": "form-control-file border"},
    )
    patient_ID = StringField(
        "patient_ID",
        validators=[DataRequired()],
        render_kw={"placeholder": "Patient ID", "class": "form-control"},
    )
    submit = SubmitField("Upload", render_kw={"class": "btn btn-primary mb-2"})


class AnnotForm(FlaskForm):
    """Form used for image annotation. Feature list are added later"""

    def __init__(self, *args, **kwargs):
        super(AnnotForm, self).__init__(*args, **kwargs)

    annotation_json = JSONField("Annotation JSON Data", render_kw={"type": "hidden"})

    submit = SubmitField(
        "Submit report and annotations to the database",
        render_kw={"class": "btn btn-primary mb-2"},
    )
    type_coloration = SelectField(
        "type_coloration",
        validators=[DataRequired()],
        choices=Common.create_list(os.path.join("config", "config_coloration.txt")),
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


class DeleteButton(FlaskForm):
    """Empty form for delete button"""

    submit = SubmitField("Confirm Deletion", render_kw={"class": "btn btn-danger"})