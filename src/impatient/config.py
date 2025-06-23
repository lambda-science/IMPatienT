import os

from dotenv import load_dotenv

# Get base working directory and load env variables
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    """Class to load all config parameters of the Flask App"""
    SECRET_KEY = os.environ.get("SECRET_KEY") or "myverylongsecretkey"

    DATA_FOLDER = os.path.join("/home/impatient", "data")
    ONTOLOGY_FOLDER = os.path.join("/home/impatient/", "data", "ontology")
    IMAGES_FOLDER = os.path.join("/home/impatient", "data", "images")
    CONFIG_FOLDER = os.path.join("/home/impatient", "src", "impatient", "config")
    VIZ_FOLDER = os.path.join("/home/impatient", "src", "impatient", "app", "static", "viz")

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

    # Max upload size: 1GB
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024

    # DB connection settings
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        "/home/impatient", "data", "database", "app.db"
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
    ONTO_SCHEMA = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "pattern": "^.*[:|_].*$"},
                "text": {"type": "string"},
                "icon": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "synonymes": {"type": "string"},
                        "phenotype_datamined": {"type": "string"},
                        "gene_datamined": {"type": "string"},
                        "alternative_language": {"type": "string"},
                        "correlates_with": {"type": "string"},
                        "image_annotation": {"type": "boolean"},
                        "hex_color": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"},
                        "hpo_datamined": {"type": "string"},
                    },
                    "required": [
                        "description",
                        "synonymes",
                        "phenotype_datamined",
                        "gene_datamined",
                        "alternative_language",
                        "correlates_with",
                        "image_annotation",
                        "hex_color",
                        "hpo_datamined",
                    ],
                },
                "parent": {"type": "string", "pattern": "[^.*[:|_].*$|^#$]]"},
            },
            "required": ["id", "text", "icon", "data", "parent"],
        },
    }
