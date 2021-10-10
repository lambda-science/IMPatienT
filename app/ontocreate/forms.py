from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField


class OntologyDescript(FlaskForm):
    """Form used to save modification of nodes in the onotlogy create tool"""

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
    parent_id = StringField(
        "Parent Vocabulary ID",
        render_kw={
            "placeholder": "Parent Vocabulary ID",
            "class": "form-control",
            "readonly": "",
        },
    )

    synonymes = StringField(
        "Synonyms", render_kw={"placeholder": "Synonyms", "class": "form-control"}
    )
    gene = StringField(
        "Associated Genes",
        render_kw={"placeholder": "Associated Genes", "class": "form-control"},
    )

    gene_datamined = StringField(
        "Associated Genes (Datamined)",
        render_kw={
            "placeholder": "Associated Genes (Datamined)",
            "class": "form-control",
            "readonly": "",
        },
    )

    phenotype = StringField(
        "Associated Phenotype",
        render_kw={"placeholder": "Associated Phenotype", "class": "form-control"},
    )

    phenotype_datamined = StringField(
        "Associated Phenotype (Datamined)",
        render_kw={
            "placeholder": "Associated Phenotype (Datamined)",
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
        },
    )
