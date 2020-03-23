#!/usr/bin/python3

# # # # #
# RangiRangi
# A simple flask based Microblogging CMS written in Python
# Coded by AlefMim (github.com/alefmim)
# Contact me at mralefmim@gmail.com
# # # # # # # # # #

import os
import re
import datetime
import jdatetime
import json
import hashlib
import urllib.parse
import functools
import logging

from flask import (
    Flask,
    render_template,
    request,
    Response,
    Markup,
    redirect,
    url_for,
    abort,
    escape,
    session,
    flash,
)
from wtforms.validators import (
    InputRequired,
    DataRequired,
    Optional,
    Email,
    URL,
    Length,
    NumberRange,
    AnyOf,
    EqualTo,
    ValidationError,
)
from wtforms.fields.html5 import (
    EmailField,
    URLField,
)
from wtforms.widgets import (
    HiddenInput,
    TextArea,
)
from wtforms import (
    SelectField,
    StringField,
    IntegerField,
    PasswordField,
    TextAreaField,
)
from flask_wtf.csrf import (
    CSRFProtect,
    CSRFError,
)
from flask_wtf import FlaskForm
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from random import randrange
from werkzeug.middleware.proxy_fix import ProxyFix
from logging.handlers import RotatingFileHandler


def create_app(test_config=None):
    '''Creates and configures an instance of the Flask application.'''
    # Initializations and Basic Configurations
    app = Flask(__name__)
    # Database connection string
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
    # Because we don't need it
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
    # This will prevent some attacks
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    # Flask-Caching related configs
    app.config["CACHE_TYPE"] = "simple"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 300
    # Assign a 32 bytes length random value to app.secret_key
    app.secret_key = os.urandom(32)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    # Return app
    return app


# def create_app(test_config=None):
#     '''Create and configure an instance of the Flask application.'''
#     global app
#     return app

# # If this module is the main program!
# if __name__ == '__main__':
#     # Run the program (For development purposes only!)
#     app.run(debug=True)
