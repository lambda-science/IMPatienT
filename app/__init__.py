import logging
import dash
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_session import Session
from config import Config
from sqlalchemy import MetaData

from flask.helpers import get_root_path
from flask_login import login_required

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Create instance of various object of our webapp.
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"
login.login_message_category = "info"
mail = Mail()
session = Session()


def create_app(config_class=Config):
    """Function used to create instance of web-app with config settings"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    with app.app_context():
        if db.engine.url.drivername == "sqlite":
            migrate.init_app(app, db, render_as_batch=True)
        else:
            migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    session.init_app(app)
    register_dashapps(app)

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

    from app.dashapp import bp as dashapp_bp

    app.register_blueprint(dashapp_bp)

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
                subject="MYO-xIA Failure",
                credentials=auth,
                secure=secure,
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # Create logs folder to log errors & log them.
        if app.config["LOG_TO_STDOUT"]:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists("logs"):
                os.mkdir("logs")
            file_handler = RotatingFileHandler(
                "logs/MYOxIA.log", maxBytes=10240, backupCount=10
            )
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s: %(message)s "
                    "[in %(pathname)s:%(lineno)d]"
                )
            )
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("MYO-xIA startup")
    return app


def register_dashapps(app):
    from app.dashapp.layout import (
        layout,
        get_external_stylesheets,
    )
    from app.dashapp.callbacks import register_callbacks

    # Meta tags for viewport responsiveness
    meta_viewport = {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1, shrink-to-fit=no",
    }
    dashapp = dash.Dash(
        __name__,
        server=app,
        url_base_pathname="/dashboard/",
        meta_tags=[meta_viewport],
        external_stylesheets=get_external_stylesheets(),
    )

    with app.app_context():
        dashapp.title = "Dashapp 1"
        dashapp.layout = layout
        register_callbacks(dashapp)
    _protect_dashviews(dashapp)


def _protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.url_base_pathname):
            dashapp.server.view_functions[view_func] = login_required(
                dashapp.server.view_functions[view_func]
            )


from app import models
