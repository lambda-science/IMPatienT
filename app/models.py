import datetime
from time import time

import jwt
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login_manager


class User(UserMixin, db.Document):
    """Database table for Users"""

    username = db.StringField(max_length=64, unique=True, required=True)
    email = db.StringField(max_length=120, unique=True, required=True)
    password_hash = db.StringField(max_length=128)
    datetime = db.DateTimeField(default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<User {} Email {}>".format(self.username, self.email)

    def set_password(self, password):
        """Method to hash password to the database

        Args:
            password (str): Plain-text password
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Method to check if the plain-text password matches the hashed one

        Args:
            password (str): Plain-text password

        Returns:
            bool: True if the password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        """Generate a JWT Token to reset password.

        Args:
            expires_in (int, optional): Token validity duration. Defaults to 600.

        Returns:
            JWT Token: The generated token as string
        """
        return jwt.encode(
            {"reset_password": str(self.id), "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token):
        """Method to check if the token is valid

        Args:
            token (JWT Token): The token to check

        Returns:
            SQLAlchemy Obj: Return the user database entry object if the token is
            valid, None otherwise
        """
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except:
            return
        return User.objects(id=id).first()

    @staticmethod
    def create_admin_account():
        """Create a default admin account if no user is present in the database"""
        user_entry = User.objects.all()
        if not user_entry:
            user = User(
                username=current_app.config["DEFAULT_ADMIN_USERNAME"],
                email=current_app.config["DEFAULT_ADMIN_EMAIL"],
            )
            user.set_password(current_app.config["DEFAULT_ADMIN_PASSWORD"])
            user.save()


@login_manager.user_loader
def load_user(id):
    """Method to load current user in Flask-Login

    Args:
        id (str): User ID in database

    Returns:
        SQLAlchemy Obj: Return the user database entry object corresponding to the ID
    """
    u = User.objects(id=id).first()
    return u


class Image(db.Document):
    """Database table for Image & annotations"""

    image_name = db.StringField(max_length=140)
    owner = db.ReferenceField(User)
    patient_id = db.StringField(max_length=140)
    biopsy_id = db.StringField(max_length=140)
    type_coloration = db.StringField(max_length=140)
    age_at_biopsy = db.IntField(min_value=-1, max_value=200, default=-1)
    image_path = db.StringField(max_length=4096, unique=True)
    diagnostic = db.StringField(max_length=140)
    datetime = db.DateTimeField(default=datetime.datetime.utcnow)
    meta = {"allow_inheritance": True}

    def __repr__(self):
        return "<Image Name {} Patient {}>".format(self.image_name, self.patient_id)

    def isduplicated(self):
        """Method to check if the image is already in the
        database (same name and patient ID)

        Returns:
            bool: True if the image is already in the database, False otherwise
        """
        if (
            Image.objects(
                image_name=self.image_name, patient_id=self.patient_id
            ).first()
            is None
        ):
            return False
        else:
            return True


class ReportHisto(db.Document):
    """Database table text reports"""

    patient_id = db.StringField(max_length=140)
    owner = db.ReferenceField(User)
    biopsie_id = db.StringField(max_length=140)
    muscle_prelev = db.StringField(max_length=140)
    age_biopsie = db.IntField(min_value=-1, max_value=200, default=-1)
    date_envoie = db.StringField(max_length=140)
    gene_diag = db.StringField(max_length=140)
    mutation = db.StringField(max_length=140)
    pheno_terms = db.StringField(max_length=4096)
    ontology_tree = db.ListField(default=[])
    comment = db.StringField(max_length=4096, default="")
    conclusion = db.StringField(max_length=140)
    BOQA_prediction = db.StringField(max_length=140)
    BOQA_prediction_score = db.FloatField()
    datetime = db.DateTimeField(default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<ReportHisto ID {} ID {} Biopsie {}>".format(
            self.id, self.patient_id, self.biopsie_id
        )
