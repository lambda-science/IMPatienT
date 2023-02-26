import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler
from redis import Redis
import rq

from config import Config
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_session import Session
from flask_mongoengine import MongoEngine

migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"
mail = Mail()
session = Session()
db = MongoEngine()


def create_app(config_class=Config):
    """Function used to create instance of web-app with config settings

    Args:
        config_class (Config Class, optional): The class containing all the
        configurations for the flask app. Defaults to Config.

    Returns:
        Flask app object: the application object of Flask
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    login_manager.init_app(app)
    mail.init_app(app)
    session.init_app(app)
    db.init_app(app)

    app.redis = Redis(
        host=app.config["REDIS_HOST"],
        port=app.config["REDIS_PORT"],
        password=app.config["REDIS_PASSWORD"],
    )
    app.task_queue = rq.Queue("impatient-tasks", connection=app.redis)

    # Configuration of our various flask-blueprint folders
    from app.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp

    app.register_blueprint(auth_bp)

    from app.index import bp as index_bp

    app.register_blueprint(index_bp)

    from app.ontocreate import bp as ontocreate_bp

    app.register_blueprint(ontocreate_bp)

    from app.historeport import bp as historeport_bp

    app.register_blueprint(historeport_bp)

    from app.histostats import bp as histostats_bp

    app.register_blueprint(histostats_bp)

    from app.imgupload import bp as imgupload_bp

    app.register_blueprint(imgupload_bp)

    # If app in production settings:
    # configure our SMTP mail connection
    # configure error-logging service
    if not app.debug and not app.testing:
        # Mail service
        if app.config["MAIL_SERVER"]:
            auth = None
            if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
                auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            secure = None
            if app.config["MAIL_USE_TLS"]:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr="no-reply@" + app.config["MAIL_SERVER"],
                toaddrs=app.config["ADMINS_EMAIL"],
                subject="IMPatienT Failure",
                credentials=auth,
                secure=secure,
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # Create logs folder to log errors & log them.
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/impatient.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("IMPatienT startup")
    return app


from app import models
