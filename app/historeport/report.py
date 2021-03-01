import pandas as pd
from flask import current_app
from glob import glob

from wtforms import BooleanField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired
import app.src.common as Common
import os
#from app import db


def generate_historeportForm(formClass,
                             report_config_file,
                             report_db_entry=None):
    # Iterative form field adding for each feature annotation in the config file feature list.
    # Loop to add attribute to form class
    df = pd.read_csv(report_config_file, sep="\t")
    list_section = []
    list_feature_cat = []
    if report_db_entry != None:
        for value in report_db_entry:
            if value == "":
                pass
            else:
                print("none")
    else:
        for index, row in df.iterrows():
            for feature in row[2:]:
                if type(feature) == str:
                    list_section.append(row[0])
                    list_feature_cat.append(row[1])
                    setattr(
                        formClass,
                        str(row[0] + "_" + row[1] + "_" + feature).replace(
                            " ", "_"),
                        BooleanField(str(feature),
                                     default=False,
                                     render_kw={"class": "btn btn-check"}))
        setattr(
            formClass, "comment",
            TextAreaField(
                render_kw={
                    "cols": "3",
                    "rows": "3",
                    "class": "form-control",
                    "placeholder": "Commentaires Divers"
                }))

        setattr(
            formClass, "conclusion",
            SelectField('diagnostic',
                        choices=Common.create_diag_list(
                            os.path.join("config", "diagnostic.tsv")),
                        render_kw={
                            "placeholder": "Conclusion Diagnosis",
                            "class": "form-control custom-select"
                        }))
        setattr(
            formClass, "submit",
            SubmitField('Submit report to the database',
                        render_kw={"class": "btn btn-primary mb-2"}))
    return (list_section, list_feature_cat)
