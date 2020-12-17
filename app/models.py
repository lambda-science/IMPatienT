from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    images = db.relationship('Image', backref='creator', lazy='dynamic')

    def __repr__(self):
        return '<User {} Email {}>'.format(self.username, self.email)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(140), index=True)
    expert_name = db.Column(db.Integer, db.ForeignKey('user.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    image_binary = db.Column(db.LargeBinary)
    diagnostic = db.Column(db.String(140), index=True)
    report_text = db.Column(db.Text)

    def __repr__(self):
        return '<Image Name {} Patient {}>'.format(self.image_name,
                                                   self.patient_id)


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_firstname = db.Column(db.String(140))
    patient_name = db.Column(db.String(140), index=True)
    images = db.relationship('Image', backref='from_patient', lazy='dynamic')

    def __repr__(self):
        return '<Patient {} {} {}>'.format(self.id, self.patient_firstname,
                                           self.patient_name)
