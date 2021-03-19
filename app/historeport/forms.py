from app.models import Patient, Image
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, SelectField, DateField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, Length
import os
from datetime import datetime
import app.src.common as Common

from wtforms import fields
import json


class JSONField(fields.StringField):
    def _value(self):
        return json.dumps(self.data) if self.data else ''

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = json.loads(valuelist[0])
            except ValueError:
                raise ValueError('This field contains invalid JSON')
        else:
            self.data = None

    def pre_validate(self, form):
        super().pre_validate(form)
        if self.data:
            try:
                json.dumps(self.data)
            except TypeError:
                raise ValueError('This field contains invalid JSON')


class ReportForm(FlaskForm):
    """Form used for report registration."""
    patient_nom = StringField('patient_nom',
                              render_kw={
                                  "placeholder": "Nom Patient",
                                  "class": "form-control"
                              })
    patient_prenom = StringField('patient_prenom',
                                 render_kw={
                                     "placeholder": "Prénom Patient",
                                     "class": "form-control"
                                 })
    naissance = StringField(
        'naissance',
        validators=[
            Regexp(
                r'(^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$)|(^$)'
            ),
            Length(max=10)
        ],
        render_kw={
            "placeholder": "Date de naissance YYYY-MM-DD",
            "class": "form-control"
        })
    biopsie_id = StringField('biopsie_id',
                             render_kw={
                                 "placeholder": "Numéro de Biopsie",
                                 "class": "form-control"
                             })
    muscle_prelev = StringField('muscle_prelev',
                                render_kw={
                                    "placeholder": "Muscle biopsie",
                                    "class": "form-control"
                                })
    age_biopsie = SelectField('Age du patient lors de la biopsie:',
                              choices=["N/A"] + [i for i in range(101)],
                              default="N/A",
                              render_kw={
                                  "placeholder":
                                  "Age du patient lors de la biopsie",
                                  "class": "form-control custom-select"
                              })
    date_envoie = StringField(
        'date_envoie',
        validators=[
            Regexp(
                r'(^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$)|(^$)'
            ),
            Length(max=10)
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "Date d'envoie rapport YYYY-MM-DD",
        })

    ontology_tree = JSONField("Json Ontolgoy Tree",
                              render_kw={"type": "hidden"})

    comment = TextAreaField("Commentaire",
                            render_kw={
                                "cols": "3",
                                "rows": "3",
                                "class": "form-control",
                                "placeholder": "Commentaires Divers"
                            })
    conclusion = SelectField('diagnostic',
                             choices=Common.create_diag_list(
                                 os.path.join("config", "diagnostic.tsv")),
                             render_kw={
                                 "placeholder": "Conclusion Diagnosis",
                                 "class": "form-control custom-select"
                             })
    submit = SubmitField('Submit report to the database',
                         render_kw={"class": "btn btn-primary mb-2"})


class OntologyDescriptPreAbs(FlaskForm):
    onto_name = StringField('Nom Terme Ontologique',
                            render_kw={
                                "placeholder": "Nom Terme Ontologique",
                                "class": "form-control",
                                "readonly": ""
                            })

    synonymes = StringField('Synonymes',
                            render_kw={
                                "placeholder": "Synonymes",
                                "class": "form-control",
                                "readonly": ""
                            })
    gene = StringField('Gene associé',
                       render_kw={
                           "placeholder": "Gene associé",
                           "class": "form-control",
                           "readonly": ""
                       })
    description = TextAreaField('Description',
                                render_kw={
                                    "placeholder": "Description",
                                    "class": "form-control",
                                    "cols": "3",
                                    "rows": "5",
                                    "readonly": "",
                                })
    presence_absence = RadioField("Status_feature",
                                  choices=[('1', 'Present'), ('-1', 'Absent'),
                                           ('0', 'Unknown')],
                                  validators=[DataRequired()])
