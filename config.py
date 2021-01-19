import os
import app.histofunc as Histofunc

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'myverylongsecretkey'
    ALLOWED_EXTENSIONS = ["tif", "tiff", "png", "jpg", "jpeg"]
    UPLOAD_FOLDER = os.path.join(basedir, "temp")
    REPORT_FOLDER = os.path.join(basedir, "results")

    FEATURE_LIST = Histofunc.create_feature_list(
        os.path.join("config", "config_ontology.tsv"))
    DIAG_LIST = Histofunc.create_diag_list(
        os.path.join("config", "diagnostic.tsv"))
    LANG_LIST = Histofunc.create_lang_list(
        os.path.join("config", "config_lang_ocr.tsv"))

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SEND_FILE_MAX_AGE_DEFAULT = 0

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['corentin.meyer@etu.unistra.fr']