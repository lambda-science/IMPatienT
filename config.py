import os
from dotenv import load_dotenv
import app.src.common as Common

# Get base working directory and load env variables
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    """Class to load all config parameters of the Flask App"""

    DEFAULT_ADMIN_USERNAME = os.environ.get("DEFAULT_ADMIN_USERNAME") or "admin"
    DEFAULT_ADMIN_EMAIL = os.environ.get("DEFAULT_ADMIN_EMAIL") or "admin@admin.admin"
    DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD") or "admin"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "myverylongsecretkey"
    DATA_FOLDER = os.path.join(basedir, "data")
    ONTOLOGY_FOLDER = os.path.join(basedir, "data", "ontology")
    IMAGES_FOLDER = os.path.join(basedir, "data", "images")
    CONFIG_FOLDER = os.path.join(basedir, "config")
    VIZ_FOLDER = os.path.join(basedir, "app", "static", "viz")
    SEND_FILE_MAX_AGE_DEFAULT = 0
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = "True"

    # Session saving on filesystem instead of user cookie
    SESSION_TYPE = "filesystem"

    # Max upload size: 1GB
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024
    # Create various list from config file
    DIAG_LIST = Common.create_diag_list(os.path.join("config", "diagnostic.tsv"))

    # DB connection settings
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        basedir, "data", "database", "app.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail Settings from environnement variables
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS_EMAIL = [os.environ.get("ADMINS_EMAIL")]

    # Heroku to STDOut
    LOG_TO_STDOUT = os.environ.get("LOG_TO_STDOUT")
