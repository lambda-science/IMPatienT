import pandas as pd
from flask import current_app
from glob import glob

from wtforms import RadioField
from wtforms.validators import DataRequired


def generate_featureForm(formClass, report=None, feature_list=[]):
    # Iterative form field adding for each feature annotation in the config file feature list.
    # Loop to add attribute to form class
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
        for feature in feature_list:
            setattr(
                formClass, feature[0],
                RadioField(feature[1],
                           choices=[('1', 'Present'), ('-1', 'Absent'),
                                    ('0', 'Uncertain')],
                           default='-1',
                           validators=[DataRequired()]))
