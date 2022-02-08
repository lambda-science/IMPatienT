import json
import os

import app.src.common as Common
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SelectField, StringField, SubmitField, TextAreaField, fields
from wtforms.fields.html5 import DecimalRangeField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp


class JSONField(fields.StringField):
    """Extension of WTForms string field to handle JSON data.

    Args:
        fields (WTForm object): StringField object of WTForms

    Raises:
        ValueError: If JSON data is invalid

    Returns:
        str: JSON data as string
    """

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
    """Form for textual reports.

    Args:
        FlaskForm (FlaskForm Class): The FlaskForm Class
    """

    patient_id = StringField(
        "Patient ID",
        validators=[Regexp(r"^[\w.-_]*$")],
        render_kw={"placeholder": "Patient ID", "class": "form-control"},
    )
    biopsie_id = StringField(
        "Biopsy ID",
        # validators=[Regexp(r"^[\w.-_]*$")],
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
        render_kw={
            "class": "form-control",
            "placeholder": "YYYY-MM-DD",
        },
    )
    mutation = StringField(
        "Mutation",
        validators=[
            Length(max=140),
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "Mutation (HGVS Format)",
        },
    )

    pheno_terms = StringField(
        "HPO Phenotype terms",
        render_kw={
            "class": "form-control",
            "placeholder": "HPO Phenotype Description",
        },
    )

    gene_diag = SelectField(
        "Diagnosed Gene",
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
    # submit = SubmitField(
    #     "Save report to the database", render_kw={"class": "btn btn-primary mb-2"}
    # )


class OntologyDescriptPreAbs(FlaskForm):
    """Form used to show informations about the ontology tree selected node.

    Args:
        FlaskForm (FlaskForm Class): The FlaskForm Class
    """

    onto_id_ext = StringField(
        "Vocabulary ID",
        render_kw={
            "placeholder": "Vocabulary ID",
            "class": "form-control",
            "readonly": "",
        },
    )
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
    # gene = StringField(
    #     "Associated Genes (Reviewed)",
    #     render_kw={
    #         "placeholder": "Associated Genes (Reviewed)",
    #         "class": "form-control",
    #         "readonly": "",
    #     },
    # )
    gene_datamined = StringField(
        "Associated Genes (Extracted from reports)",
        render_kw={
            "placeholder": "Associated Genes (Extracted from reports)",
            "class": "form-control",
            "readonly": "",
        },
    )

    # phenotype = StringField(
    #     "Associated Phenotype (Reviewed)",
    #     render_kw={"placeholder": "Associated Phenotype (Reviewed)", "class": "form-control", "readonly": "",},
    # )

    phenotype_datamined = StringField(
        "Associated Disease (Extracted from reports)",
        render_kw={
            "placeholder": "Associated Disease (Extracted from reports)",
            "class": "form-control",
            "readonly": "",
        },
    )
    alternative_language = StringField(
        "Alternative Language",
        render_kw={
            "placeholder": "Alternative Language",
            "class": "form-control",
            "readonly": "",
        },
    )
    correlates_with = StringField(
        "Positively Correlates with (Extracted from reports ; >0.5)",
        render_kw={
            "placeholder": "Positively Correlates with (Extracted from reports ; >0.5)",
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
        render_kw={
            "min": -0.25,
            "max": 1,
            "step": 0.25,
            "class": "form-range",
        },
    )


class DeleteButton(FlaskForm):
    """Empty form for the delete button.

    Args:
        FlaskForm (FlaskForm Class): The FlaskForm Class
    """

    submit = SubmitField("Confirm Deletion", render_kw={"class": "btn btn-danger"})


class PdfUpload(FlaskForm):
    """Form for uploading images.

    Args:
        FlaskForm (FlaskForm Class): The FlaskForm Class
    """

    pdf_file = FileField(
        validators=[
            FileRequired(),
            FileAllowed(
                ["pdf"],
                "This file is not a valid image !",
            ),
        ],
        render_kw={"class": "form-control-file border"},
    )
    language = SelectField(
        "language",
        validators=[DataRequired()],
        choices=[
            ("eng", "English"),
            ("fra", "French"),
        ],
        render_kw={
            "placeholder": "PDF Language",
            "class": "form-control custom-select",
        },
    )

    # submit = SubmitField(
    #     "Upload",
    #     render_kw={
    #         "class": "btn btn-primary mb-2",
    #     },
    # )
