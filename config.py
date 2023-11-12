# config.py

from logging.config import dictConfig
import os


class Config(object):
    """
    Common configurations
    """

    # Put any configurations here that are common across all environments

    # Name of the app
    APP_NAME = 'app'
    HOST = '127.0.0.1'
    PORT = '5000'

    # SQLite DB info
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, '{0}.db'.format(APP_NAME))

    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(db_path)
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # Threads
    THREADS_PER_PAGE = 2

    # Enable protection against *Cross-site Request Forgery (CSRF)*
    CSRF_ENABLED = True

    # Use a secure, unique and absolutely secret key for
    # signing the data. Default: MD5 of "secret"
    CSRF_SESSION_KEY = "5ebe2294ecd0e0f08eab7690d2a6ee69"

    # Secret key for signing cookies
    SECRET_KEY = "5ebe2294ecd0e0f08eab7690d2a6ee69"

    # Salt for Tokens
    SALTY_SECRET = "5ebe2294ecd0e0f08eab7690d2a6ee69"

    # Define logging dict
    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '{"date": "%(asctime)s", '
                          '"log_level": "%(levelname)s", '
                          '"module": "%(module)s", '
                          '"message": "%(message)s"}'
            }
        },
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': 'app.log',
                'maxBytes': 1024000,
                'backupCount': 3
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': [
                'wsgi',
                'file'
            ]
        }
    })


class DevelopmentConfig(Config):
    """
    Development configurations
    """

    DEBUG = True
    FLASK_DEBUG = 1
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False
    FLASK_DEBUG = 0


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

