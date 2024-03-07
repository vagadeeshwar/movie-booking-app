import os
from flask import Flask, flash, redirect, url_for
from .config import LocalDevelopmentConfig, ProductionConfig
from .database import db, create_tables
from flask_login import LoginManager
from .models import User

from .views.user_views import user_bp
from .views.venue_views import venue_bp
from .views.show_views import show_bp
from .views.booking_views import booking_bp
from .api import api_bp


def register_blueprints(app):
    app.register_blueprint(user_bp)
    app.register_blueprint(venue_bp, url_prefix="/venue")
    app.register_blueprint(show_bp, url_prefix="/show")
    app.register_blueprint(booking_bp, url_prefix="/book")
    app.register_blueprint(api_bp, url_prefix="/api")


def configure_app(app):
    if os.getenv("ENV", "development") == "production":
        print("Starting Production Server")
        app.config.from_object(ProductionConfig)
    else:
        print("Starting Local Development")
        app.config.from_object(LocalDevelopmentConfig)


def init_db(app):
    db.init_app(app)

    app.app_context().push()
    with app.app_context():
        create_tables()


def setup_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "user.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def unauthorized_callback():
        flash("Please log in to access this page.", "info")
        return redirect(url_for("user.login"))

    login_manager.unauthorized_handler(unauthorized_callback)


def create_app():
    app = Flask(__name__)
    configure_app(app)
    init_db(app)
    register_blueprints(app)
    setup_login_manager(app)

    return app
