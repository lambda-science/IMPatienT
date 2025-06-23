import datetime

from impatient.app import db


class Image(db.Model):
    """Database table for Image & annotations"""

    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(140), nullable=False)
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
