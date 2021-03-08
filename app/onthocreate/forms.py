from app.models import Patient, Image
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, RadioField, SelectField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, Length


class OntologyDescript(FlaskForm):
    onto_id_ext = StringField('ID Ontologie Externe',
                              render_kw={
                                  "placeholder": "ID Ontologie Externe",
                                  "class": "form-control",
                                  "readonly": ""
                              })
    onto_name = StringField('Nom Terme Ontologique',
                            render_kw={
                                "placeholder": "Nom Terme Ontologique",
                                "class": "form-control",
                                "readonly": ""
                            })
    parent_id = StringField('ID Parent',
                            render_kw={
                                "placeholder": "ID Parent",
                                "class": "form-control",
                                "readonly": ""
                            })

    synonymes = StringField('Synonymes',
                            render_kw={
                                "placeholder": "Synonymes",
                                "class": "form-control"
                            })
    gene = StringField('Gene associé',
                       render_kw={
                           "placeholder": "Gene associé",
                           "class": "form-control"
                       })
    description = TextAreaField('Description',
                                render_kw={
                                    "placeholder": "Description",
                                    "class": "form-control",
                                    "cols": "3",
                                    "rows": "5",
                                })
