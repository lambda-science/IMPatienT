from time import time
import jwt
from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
import os


class User(UserMixin, db.Model):
    """Database table for Users"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    images = db.relationship('Image', backref='creator', lazy='dynamic')

    def __repr__(self):
        return '<User {} Email {}>'.format(self.username, self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {
                'reset_password': self.id,
                'exp': time() + expires_in
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token,
                            current_app['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Image(db.Model):
    """Database table for Image & annotations"""
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(140), index=True)
    expert_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    patient_id = db.Column(db.String(100), db.ForeignKey('patient.id'))
    image_binary = db.Column(db.LargeBinary)
    diagnostic = db.Column(db.String(140), index=True)
    report_text = db.Column(db.Text)
    annotation_json = db.Column(db.Text, default="[]")

    def __repr__(self):
        return '<Image Name {} Patient {}>'.format(self.image_name,
                                                   self.patient_id)

    def set_imageblob(self, filename):
        with open(os.path.join(current_app.config["UPLOAD_FOLDER"], filename),
                  'rb') as file:
            self.image_binary = file.read()

    def isduplicated(self):
        if Image.query.filter_by(image_name=self.image_name,
                                 patient_id=self.patient_id).first() is None:
            return False
        else:
            return True


class Patient(db.Model):
    """Database table for Patient informations"""
    id = db.Column(db.String(100), primary_key=True)
    patient_firstname = db.Column(db.String(140))
    patient_name = db.Column(db.String(140), index=True)
    images = db.relationship('Image', backref='from_patient', lazy='dynamic')

    def __repr__(self):
        return '<Patient {} {} {}>'.format(self.id, self.patient_firstname,
                                           self.patient_name)

    def existAlready(self):
        if Patient.query.get(str(self.id)) is None:
            return False
        else:
            return True


class Pdf(db.Model):
    """Database table for PDF and OCR Results"""
    id = db.Column(db.Integer, primary_key=True)
    pdf_name = db.Column(db.String(140), index=True)
    expert_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    patient_id = db.Column(db.String(100), db.ForeignKey('patient.id'))
    pdf_binary = db.Column(db.LargeBinary)
    lang = db.Column(db.String(140), index=True)
    ocr_text = db.Column(db.Text)

    def __repr__(self):
        return '<Pdf Name {} Patient {}>'.format(self.pdf_name,
                                                 self.patient_id)

    def set_pdfblob(self, filename):
        with open(os.path.join(current_app.config["UPLOAD_FOLDER"], filename),
                  'rb') as file:
            self.pdf_binary = file.read()

    def isduplicated(self):
        if Pdf.query.filter_by(pdf_name=self.pdf_name,
                               patient_id=self.patient_id).first() is None:
            return False
        else:
            return True