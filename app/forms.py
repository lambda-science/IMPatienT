from app import app
from app.models import User, Patient, Image

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ImageForm(FlaskForm):
    image = FileField(validators=[
        FileRequired(),
        FileAllowed(app.config["ALLOWED_EXTENSIONS"],
                    "This file is not a valid image !")
    ],
                      render_kw={"class": "form-control-file"})
    patient_ID = StringField('patient_ID',
                             validators=[DataRequired()],
                             render_kw={
                                 "placeholder": "Patient ID",
                                 "class": "form-control"
                             })
    patient_nom = StringField('patient_nom',
                              validators=[DataRequired()],
                              render_kw={
                                  "placeholder": "Patient Last Name",
                                  "class": "form-control"
                              })
    patient_prenom = StringField('patient_prenom',
                                 validators=[DataRequired()],
                                 render_kw={
                                     "placeholder": "Patient First Name",
                                     "class": "form-control"
                                 })
    submit = SubmitField('Upload', render_kw={"class": "btn btn-primary mb-2"})

    def validate_patient_nom(self, patient_nom):
        patient = Patient.query.get(self.patient_ID.data)
        if patient is not None:
            if patient.patient_name != patient_nom.data:
                raise ValidationError(
                    str('Same Patient ID with different last name already exists: '
                        + patient.patient_name +
                        " ; Please use another ID or correct patient name"))

    def validate_patient_prenom(self, patient_prenom):
        patient = Patient.query.get(self.patient_ID.data)
        if patient is not None:
            if patient.patient_firstname != patient_prenom.data:
                raise ValidationError(
                    str('Same Patient ID with different firstname already exists: '
                        + patient.patient_firstname +
                        " ;  Please use another ID or correct patient name"))


class AnnotForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(AnnotForm, self).__init__(*args, **kwargs)

    submit = SubmitField('Submit report and annotations to the database',
                         render_kw={"class": "btn btn-primary mb-2"})

    diagnostic = SelectField('diagnostic',
                             validators=[DataRequired()],
                             choices=app.config["DIAG_LIST"],
                             render_kw={
                                 "placeholder": "Disease diagnostic",
                                 "class": "form-control custom-select"
                             })


for feature in app.config["FEATURE_LIST"]:
    setattr(
        AnnotForm, feature[0],
        RadioField(feature[1],
                   choices=[('1', 'Present'), ('-1', 'Absent'),
                            ('0', 'Uncertain')],
                   default='-1',
                   validators=[DataRequired()]))


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[
                               DataRequired(),
                               Regexp(r'^[\w.@+-]+$'),
                               Length(min=4, max=25)
                           ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password',
                              validators=[DataRequired(),
                                          EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already used.')


class PdfForm(FlaskForm):
    pdf = FileField(validators=[
        FileRequired(),
        FileAllowed(["pdf"], "This file is not a valid PDF File !")
    ],
                    render_kw={"class": "form-control-file"})
    patient_ID = StringField('patient_ID',
                             validators=[DataRequired()],
                             render_kw={
                                 "placeholder": "Patient ID",
                                 "class": "form-control"
                             })
    patient_nom = StringField('patient_nom',
                              validators=[DataRequired()],
                              render_kw={
                                  "placeholder": "Patient Last Name",
                                  "class": "form-control"
                              })
    patient_prenom = StringField('patient_prenom',
                                 validators=[DataRequired()],
                                 render_kw={
                                     "placeholder": "Patient First Name",
                                     "class": "form-control"
                                 })

    lang = SelectField('lang',
                       validators=[DataRequired()],
                       choices=app.config["LANG_LIST"],
                       render_kw={
                           "placeholder": "PDF Langage",
                           "class": "form-control custom-select"
                       })
    submit = SubmitField('Upload', render_kw={"class": "btn btn-primary mb-2"})

    def validate_patient_nom(self, patient_nom):
        patient = Patient.query.get(self.patient_ID.data)
        if patient is not None:
            if patient.patient_name != patient_nom.data:
                raise ValidationError(
                    str('Same Patient ID with different last name already exists: '
                        + patient.patient_name +
                        " ; Please use another ID or correct patient name"))

    def validate_patient_prenom(self, patient_prenom):
        patient = Patient.query.get(self.patient_ID.data)
        if patient is not None:
            if patient.patient_firstname != patient_prenom.data:
                raise ValidationError(
                    str('Same Patient ID with different firstname already exists: '
                        + patient.patient_firstname +
                        " ;  Please use another ID or correct patient name"))


class OcrForm(FlaskForm):
    submit = SubmitField('Submit text to database',
                         render_kw={"class": "btn btn-primary mb-2"})


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password',
                              validators=[DataRequired(),
                                          EqualTo('password')])
    submit = SubmitField('Request Password Reset')