from app import app
from app.models import User

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ImageForm(FlaskForm):
    image = FileField(validators=[
        FileRequired(),
        FileAllowed(app.config["ALLOWED_EXTENSIONS"],
                    "Ce fichier n'est pas une image valide !")
    ],
                      render_kw={"class": "form-control-file"})
    patient_ID = StringField('patient_ID',
                             validators=[DataRequired()],
                             render_kw={
                                 "placeholder": "Identifiant Patient",
                                 "class": "form-control"
                             })
    submit = SubmitField('Upload', render_kw={"class": "btn btn-primary mb-2"})


class AnnotForm(FlaskForm):
    def __init__(self, patient_id_value, *args, **kwargs):
        super(AnnotForm, self).__init__(*args, **kwargs)
        self.patient_id_value = patient_id_value
        setattr(
            AnnotForm, "patient_id",
            StringField('patient_ID',
                        render_kw={
                            "placeholder": patient_id_value,
                            "class": "form-control",
                            "readonly": "True"
                        }))

    patient_nom = StringField('patient_nom',
                              validators=[DataRequired()],
                              render_kw={
                                  "placeholder": "Nom Patient",
                                  "class": "form-control"
                              })
    patient_prenom = StringField('patient_prenom',
                                 validators=[DataRequired()],
                                 render_kw={
                                     "placeholder": "Prénom Patient",
                                     "class": "form-control"
                                 })
    expert_name = StringField('expert_name',
                              validators=[DataRequired()],
                              render_kw={
                                  "placeholder": "Nom du rapporteur",
                                  "class": "form-control",
                              })
    submit = SubmitField('Générer le rapport',
                         render_kw={"class": "btn btn-primary mb-2"})

    diagnostic = StringField('diagnostic',
                             validators=[DataRequired()],
                             render_kw={
                                 "placeholder": "Diagnostique de Maladie",
                                 "class": "form-control"
                             })


for feature in app.config["FEATURE_LIST"]:
    setattr(
        AnnotForm, feature[0],
        RadioField(feature[1],
                   choices=[('1', 'Présent'), ('-1', 'Absent'),
                            ('0', 'Incertain')],
                   default='-1',
                   validators=[DataRequired()]))


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
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