from time import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
from app import db
from app import login
import datetime


class User(UserMixin, db.Model):
    """Database table for Users"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    images = db.relationship("Image", backref="creator", lazy="dynamic")
    pdf = db.relationship("Pdf", backref="creator", lazy="dynamic")
    report = db.relationship("ReportHisto", backref="creator", lazy="dynamic")

    def __repr__(self):
        return "<User {} Email {}>".format(self.username, self.email)

    def set_password(self, password):
        """Method to hash password in DB"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Method to check plain-text password against hashed password"""
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        """Method generate a password reset token"""
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token):
        """Method to check if token is valid"""
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    """Method to load current user in flask-login"""
    return User.query.get(int(id))


class Image(db.Model):
    """Database table for Image & annotations"""

    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(140), nullable=False)
    expert_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    patient_id = db.Column(db.String(100), index=True, nullable=False)
    type_coloration = db.Column(db.String(140))
    age_at_biopsy = db.Column(db.Integer, default=-1)
    image_path = db.Column(db.String(4096), unique=True, nullable=False)
    diagnostic = db.Column(db.String(140), index=True)
    report_text = db.Column(db.Text, default="")
    annotation_json = db.Column(db.JSON, default=[])

    def __repr__(self):
        return "<Image Name {} Patient {}>".format(self.image_name, self.patient_id)

    def isduplicated(self):
        """Method to check if new entry already exist"""
        if (
            Image.query.filter_by(
                image_name=self.image_name, patient_id=self.patient_id
            ).first()
            is None
        ):
            return False
        else:
            return True


class Pdf(db.Model):
    """Database table for PDF and OCR Results"""

    id = db.Column(db.Integer, primary_key=True)
    pdf_name = db.Column(db.String(140), index=True, nullable=False)
    expert_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    patient_id = db.Column(db.String(100), index=True, nullable=False)
    pdf_path = db.Column(db.String(4096), unique=True, nullable=False)
    lang = db.Column(db.String(140), nullable=False)
    ocr_text = db.Column(db.Text, default="")

    def __repr__(self):
        return "<Pdf Name {} Patient {}>".format(self.pdf_name, self.patient_id)

    def isduplicated(self):
        """Method to check if new entry already exist"""
        if (
            Pdf.query.filter_by(
                pdf_name=self.pdf_name, patient_id=self.patient_id
            ).first()
            is None
        ):
            return False
        else:
            return True


class ReportHisto(db.Model):
    """Database table histology reports"""

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(100), index=True)
    expert_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    biopsie_id = db.Column(db.String(140))
    muscle_prelev = db.Column(db.String(140))
    age_biopsie = db.Column(db.Integer)
    date_envoie = db.Column(db.String(10))
    gene_diag = db.Column(db.String(140), index=True)
    ontology_tree = db.Column(db.JSON, default=[], nullable=False)
    comment = db.Column(db.Text, default="")
    conclusion = db.Column(db.String(140), index=True)
    datetime = db.Column(
        db.DateTime(),
        onupdate=datetime.datetime.utcnow,
        default=datetime.datetime.utcnow,
    )

    def __repr__(self):
        return "<ReportHisto ID {} ID {} Biopsie {}>".format(
            self.id, self.patient_id, self.biopsie_id
        )
