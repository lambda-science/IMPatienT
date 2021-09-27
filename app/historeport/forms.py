import os
import json
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    #    RadioField,
    SelectField,
    TextAreaField,
)
from wtforms.fields.html5 import DecimalRangeField
from wtforms.validators import DataRequired, Regexp, Length, NumberRange
from wtforms import fields
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


class ReportForm(FlaskForm):
    """Form used for report registration."""

    patient_id = StringField(
        "Patient ID",
        validators=[Regexp(r"^[\w.-_]*$")],
        render_kw={"placeholder": "Patient ID", "class": "form-control"},
    )
    biopsie_id = StringField(
        "Biopsy ID",
        validators=[Regexp(r"^[\w.-_]*$")],
        render_kw={"placeholder": "Biopsy ID", "class": "form-control"},
    )
    muscle_prelev = StringField(
        "Muscle",
        validators=[Regexp(r"^[\w.-_]*$")],
        render_kw={"placeholder": "Muscle", "class": "form-control"},
    )
    age_biopsie = SelectField(
        "Patient age at biopsy:",
        choices=["N/A"] + [i for i in range(101)],
        default="N/A",
        render_kw={
            "placeholder": "Patient age at biopsy",
            "class": "form-control custom-select",
        },
    )
    date_envoie = StringField(
        "Biopsy Date",
        validators=[
            Regexp(r"(^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$)|(^$)"),
            Length(max=10),
        ],
        render_kw={"class": "form-control", "placeholder": "YYYY-MM-DD",},
    )
    gene_diag = SelectField(
        "Diagnosed Gene ",
        validators=[DataRequired()],
        choices=Common.create_list(os.path.join("config", "config_gene.txt")),
        render_kw={
            "placeholder": "Diagnosed Gene",
            "class": "form-control custom-select",
        },
    )
    ontology_tree = JSONField("Json Ontology Tree", render_kw={"type": "hidden"})

    comment = TextAreaField(
        "Commentary",
        render_kw={
            "cols": "3",
            "rows": "3",
            "class": "form-control",
            "placeholder": "Commentary",
        },
    )
    conclusion = SelectField(
        "Final Diagnosis",
        choices=Common.create_diag_list(os.path.join("config", "diagnostic.tsv")),
        render_kw={
            "placeholder": "Final Diagnosis",
            "class": "form-control custom-select",
        },
    )
    submit = SubmitField(
        "Save report to the database", render_kw={"class": "btn btn-primary mb-2"}
    )


class OntologyDescriptPreAbs(FlaskForm):
    """Form used to show node informations from ontology tree"""

    onto_name = StringField(
        "Vocabulary Name",
        render_kw={
            "placeholder": "Vocabulary Name",
            "class": "form-control",
            "readonly": "",
        },
    )

    synonymes = StringField(
        "Synonyms",
        render_kw={"placeholder": "Synonyms", "class": "form-control", "readonly": ""},
    )
    gene = StringField(
        "Associated Genes",
        render_kw={
            "placeholder": "Associated Genes",
            "class": "form-control",
            "readonly": "",
        },
    )
    description = TextAreaField(
        "Description",
        render_kw={
            "placeholder": "Description",
            "class": "form-control",
            "cols": "3",
            "rows": "5",
            "readonly": "",
        },
    )
    preabsProba = DecimalRangeField(
        "Absence / Presence",
        validators=[NumberRange(min=-0.25, max=1)],
        render_kw={"min": -0.25, "max": 1, "step": 0.25, "class": "form-range",},
    )


class DeleteButton(FlaskForm):
    """Empty form for delete button"""

    submit = SubmitField("Confirm Deletion", render_kw={"class": "btn btn-danger"})
