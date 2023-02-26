import os

from dotenv import load_dotenv

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
    TEXT_FOLDER = os.path.join(basedir, "data", "images")
    CONFIG_FOLDER = os.path.join(basedir, "config")
    VIZ_FOLDER = os.path.join(basedir, "app", "static", "viz")

    negex_en = open(os.path.join(CONFIG_FOLDER, "negex_en.txt"), "r")
    negex_fr = open(os.path.join(CONFIG_FOLDER, "negex_fr.txt"), "r")
    NEGEX_LIST_EN = [line.strip("\n") for line in negex_en.readlines()]
    NEGEX_LIST_FR = [line.strip("\n") for line in negex_fr.readlines()]

    negex_sent_en = open(os.path.join(CONFIG_FOLDER, "negex_sep_en.txt"), "r")
    negex_sent_fr = open(os.path.join(CONFIG_FOLDER, "negex_sep_fr.txt"), "r")
    NEGEX_SENT_EN = [line.strip("\n") for line in negex_sent_en.readlines()]
    NEGEX_SENT_FR = [line.strip("\n") for line in negex_sent_fr.readlines()]

    SEND_FILE_MAX_AGE_DEFAULT = 0
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = "True"

    # Session saving on filesystem instead of user cookie
    SESSION_TYPE = "filesystem"

    # Max upload size: 512MB
    MAX_CONTENT_LENGTH = 1024 * 1024 * 512

    # DB connection settings
    MONGODB_SETTINGS = {
        "host": os.environ.get("MONGODB_HOST"),
    }

    # Mail Settings from environnement variables
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS_EMAIL = [os.environ.get("ADMINS_EMAIL")]
