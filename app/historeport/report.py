import pandas as pd
from flask import current_app
from glob import glob

from wtforms import BooleanField
from wtforms.validators import DataRequired


def generate_historeportForm(formClass, report_config_file, report=None):
    # Iterative form field adding for each feature annotation in the config file feature list.
    # Loop to add attribute to form class
    df = pd.read_csv(report_config_file, sep="\t")
    if report != None:
        for lines in report.split("\n"):
            if lines == "":
                pass
            else:
                feature = lines.split("\t")
                setattr(
                    formClass, feature[0],
                    RadioField(feature[0].replace("_", " "),
                               choices=[('1', 'Present'), ('-1', 'Absent'),
                                        ('0', 'Uncertain')],
                               default=feature[1],
                               validators=[DataRequired()]))
    else:
        for feature in df:
            setattr(
                formClass, feature.replace(" ","_"),
                BooleanField(str(feature), default=False, render_kw={"class": "btn-check"}))
