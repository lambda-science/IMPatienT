import datetime
from time import time

import jwt
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login_manager


class User(UserMixin, db.Model):
    """Database table for Users"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(
        db.String(64),
        index=True,
        unique=True,
        nullable=False,
    )
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    images = db.relationship("Image", backref="creator", lazy="dynamic")
    report = db.relationship("ReportHisto", backref="creator", lazy="dynamic")

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
            {"reset_password": self.id, "exp": time() + expires_in},
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
        return User.query.get(id)

    @staticmethod
    def create_admin_account():
        """Create a default admin account if no user is present in the database"""
        user_entry = User.query.get(1)
        if not user_entry:
            user = User(
                username=current_app.config["DEFAULT_ADMIN_USERNAME"],
                email=current_app.config["DEFAULT_ADMIN_EMAIL"],
            )
            user.set_password(current_app.config["DEFAULT_ADMIN_PASSWORD"])
            db.session.add(user)
            db.session.commit()


@login_manager.user_loader
def load_user(id):
    """Method to load current user in Flask-Login

    Args:
        id (str): User ID in database

    Returns:
        SQLAlchemy Obj: Return the user database entry object corresponding to the ID
    """
    return User.query.get(int(id))


class Image(db.Model):
    """Database table for Image & annotations"""

    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(140), nullable=False)
    expert_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    patient_id = db.Column(db.String(100), index=True, nullable=False)
    biopsy_id = db.Column(db.String(100), index=True)
    type_coloration = db.Column(db.String(140))
    age_at_biopsy = db.Column(db.Integer, default=-1)
    image_path = db.Column(db.String(4096), unique=True, nullable=False)
    image_background_path = db.Column(db.String(4096), unique=True)
    sigma_range_min = db.Column(db.Float())
    sigma_range_max = db.Column(db.Float())
    diagnostic = db.Column(db.String(140), index=True)
    seg_matrix_path = db.Column(db.String(4096), unique=True)
    mask_image_path = db.Column(db.String(4096), unique=True)
    blend_image_path = db.Column(db.String(4096), unique=True)
    classifier_path = db.Column(db.String(4096), unique=True)
    mask_annot_path = db.Column(db.String(4096), unique=True)
    class_info_path = db.Column(db.String(4096), unique=True)
    datetime = db.Column(
        db.DateTime(),
        onupdate=datetime.datetime.utcnow,
        default=datetime.datetime.utcnow,
    )

    def __repr__(self):
        return "<Image Name {} Patient {}>".format(self.image_name, self.patient_id)

    def isduplicated(self):
        """Method to check if the image is already in the
        database (same name and patient ID)

        Returns:
            bool: True if the image is already in the database, False otherwise
        """
        if (
            Image.query.filter_by(
                image_name=self.image_name, patient_id=self.patient_id
            ).first()
            is None
        ):
            return False
        else:
            return True


class ReportHisto(db.Model):
    """Database table text reports"""

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(100), index=True)
    expert_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    biopsie_id = db.Column(db.String(140))
    muscle_prelev = db.Column(db.String(140))
    age_biopsie = db.Column(db.Integer)
    date_envoie = db.Column(db.String(10))
    gene_diag = db.Column(db.String(140), index=True)
    mutation = db.Column(db.String(140))
    pheno_terms = db.Column(db.String(4096))
    ontology_tree = db.Column(db.JSON, default=[], nullable=False)
    comment = db.Column(db.Text, default="")
    conclusion = db.Column(db.String(140), index=True)
    BOQA_prediction = db.Column(db.String(140), index=True)
    BOQA_prediction_score = db.Column(db.Float())
    datetime = db.Column(
        db.DateTime(),
        onupdate=datetime.datetime.utcnow,
        default=datetime.datetime.utcnow,
    )

    def __repr__(self):
        return "<ReportHisto ID {} ID {} Biopsie {}>".format(
            self.id, self.patient_id, self.biopsie_id
        )
