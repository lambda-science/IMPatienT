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
        "ID Patient", render_kw={"placeholder": "ID Patient", "class": "form-control"}
    )
    biopsie_id = StringField(
        "Numéro de Biopsie",
        render_kw={"placeholder": "Numéro de Biopsie", "class": "form-control"},
    )
    muscle_prelev = StringField(
        "Muscle prélevé",
        render_kw={"placeholder": "Muscle prélevé", "class": "form-control"},
    )
    age_biopsie = SelectField(
        "Âge du patient lors de la biopsie:",
        choices=["N/A"] + [i for i in range(101)],
        default="N/A",
        render_kw={
            "placeholder": "Age du patient lors de la biopsie",
            "class": "form-control custom-select",
        },
    )
    date_envoie = StringField(
        "Date d'envoi ou de biopsie",
        validators=[
            Regexp(r"(^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$)|(^$)"),
            Length(max=10),
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "YYYY-MM-DD",
        },
    )
    gene_diag = SelectField(
        "Gène diagnostiqué",
        validators=[DataRequired()],
        choices=Common.create_list(os.path.join("config", "config_gene.txt")),
        render_kw={
            "placeholder": "Gene diagnostiqué",
            "class": "form-control custom-select",
        },
    )
    ontology_tree = JSONField("Json Ontology Tree", render_kw={"type": "hidden"})

    comment = TextAreaField(
        "Commentaire",
        render_kw={
            "cols": "3",
            "rows": "3",
            "class": "form-control",
            "placeholder": "Commentaires Divers",
        },
    )
    conclusion = SelectField(
        "Diagnostic final",
        choices=Common.create_diag_list(os.path.join("config", "diagnostic.tsv")),
        render_kw={
            "placeholder": "Conclusion Diagnosis",
            "class": "form-control custom-select",
        },
    )
    submit = SubmitField(
        "Submit report to the database", render_kw={"class": "btn btn-primary mb-2"}
    )


class OntologyDescriptPreAbs(FlaskForm):
    """Form used to show node informations from ontology tree"""

    onto_name = StringField(
        "Nom Terme Ontologique",
        render_kw={
            "placeholder": "Nom Terme Ontologique",
            "class": "form-control",
            "readonly": "",
        },
    )

    synonymes = StringField(
        "Synonymes",
        render_kw={"placeholder": "Synonymes", "class": "form-control", "readonly": ""},
    )
    gene = StringField(
        "Gene associé",
        render_kw={
            "placeholder": "Gene associé",
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
        "Obtainability / Presence",
        validators=[NumberRange(min=-1, max=1)],
        render_kw={
            "min": -1.25,
            "max": 1,
            "step": 0.25,
            "class": "form-range",
        },
    )


class DeleteButton(FlaskForm):
    """Empty form for delete button"""

    submit = SubmitField("Confirm Deletion", render_kw={"class": "btn btn-danger"})
