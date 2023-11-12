# Import the Flask basics
from flask import Flask, flash, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate

import logging

# local imports
from config import app_config

# Define the DB
db = SQLAlchemy()

# Setup a Flask-Login Manager
login_manager = LoginManager()


def create_app(config_name):

    # Define the App
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('../config.py')

    Bootstrap(app)
    db.init_app(app)
    login_manager.init_app(app)

    # Migrate DB to fix any changes
    migrate = Migrate(app, db)
    # Pull in the data model for Alembic
    from base_app.auth.models import User, Role
    from base_app.data.models import Quotes

    #
    # Module Imports
    #

    # Import the module / component using their blueprints
    from base_app.home.views import home
    from base_app.auth.views import auth
    from base_app.api.views import api_bp

    # Register Blueprints
    app.register_blueprint(home)
    app.register_blueprint(auth)
    app.register_blueprint(api_bp)

    # Flask module stuff
    @app.after_request
    def add_header(response):
        """ added for auth issue where users are logged in
         and seeing other users profiles """
        response.cache_control.private = True
        response.cache_control.public = False
        return response
    #
    # @login_manager.unauthorized_callback
    # def unauthorized_callback():
    #     """"  Handle unauthorized sessions better by
    #     redirecting to index """
    #     flash("You have either been logged out "
    #           "or you are unauthorized. Please Sign In")
    #     return redirect(url_for('home.index'))

    # For Flask shell if needed
    @app.shell_context_processor
    def make_shell_context():
        return dict(
            db=db,
            User=User,
            Role=Role,
            Quotes=Quotes
        )

    return app





