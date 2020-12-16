import os
import app.histofunc as Histofunc


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'myverylongsecretkey'
    ALLOWED_EXTENSIONS = ["tif", "tiff", "png", "jpg", "jpeg"]
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    REPORT_FOLDER = os.path.join(os.getcwd(), "results")
    FEATURE_LIST = Histofunc.create_feature_list(
        os.path.join("config", "config_ontology.tsv"))
