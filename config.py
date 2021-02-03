import os
import app.src.common as Common
from dotenv import load_dotenv

# Get base working directory and load env variables
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'myverylongsecretkey'
    ALLOWED_EXTENSIONS = ["tif", "tiff", "png", "jpg", "jpeg"]
    TEMP_FOLDER = os.path.join(basedir, "temp")
    DATA_FOLDER = os.path.join(basedir, "data")
    # Session saving on memory instead of user cookie
    SESSION_TYPE = "filesystem"

    # Create various list from config file
    FEATURE_LIST = Common.create_feature_list(
        os.path.join("config", "config_ontology.tsv"))
    DIAG_LIST = Common.create_diag_list(
        os.path.join("config", "diagnostic.tsv"))
    LANG_LIST = Common.create_lang_list(
        os.path.join("config", "config_lang_ocr.tsv"))

    # DB connection settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail Settings from environnement variables
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['corentin.meyer@etu.unistra.fr']

    # Heroku to STDOut
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')