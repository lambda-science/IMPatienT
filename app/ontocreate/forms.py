from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField


class OntologyDescript(FlaskForm):
    """Form used to show and save modification of nodes from the standard vocabulary
    tree in the standard vocabulary creator module

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
    # gene = StringField(
    #     "Associated Genes (Reviewed)",
    #     render_kw={"placeholder": "Associated Genes (Reviewed)", "class": "form-control"},
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
    #     "Associated Phenotype",
    #     render_kw={"placeholder": "Associated Phenotype", "class": "form-control"},
    # )

    phenotype_datamined = StringField(
        "Associated Disease (Extracted from reports)",
        render_kw={
            "placeholder": "Associated Disease (Extracted from reports)",
            "class": "form-control",
            "readonly": "",
        },
    )
    hpo_datamined = StringField(
        "Associated HPO Terms (Extracted from reports)",
        render_kw={
            "placeholder": "Associated HPO Terms (Extracted from reports)",
            "class": "form-control",
            "readonly": "",
        },
    )
    alternative_language = StringField(
        "Alternative Language",
        render_kw={
            "placeholder": "Alternative Language",
            "class": "form-control",
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
        },
    )


class InvertLangButton(FlaskForm):
    """Empty form for the langage inversion button.

    Args:
        FlaskForm (FlaskForm Class): The FlaskForm Class
    """

    submit = SubmitField("Confirm Inversion", render_kw={"class": "btn btn-warning"})
