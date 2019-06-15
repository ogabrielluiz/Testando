from flask import Flask
from config import Config
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_bootstrap import Bootstrap
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

App = Flask(__name__)
mongo = PyMongo()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    mongo.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:
        if App.config['MAIL_SERVER']:
            auth = None
            if App.config['MAIL_USERNAME'] or App.config['MAIL_PASSWORD']:
                auth = (App.config['MAIL_USERNAME'], App.config['MAIL_PASSWORD'])
            secure = None
            if App.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(App.config['MAIL_SERVER'], App.config['MAIL_PORT']),
                fromaddr='no-reply@' + App.config['MAIL_SERVER'],
                toaddrs=App.config['ADMINS'], subject='Testando Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            App.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/testando.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))

        file_handler.setLevel(logging.INFO)
        App.logger.addHandler(file_handler)

        App.logger.setLevel(logging.INFO)
        App.logger.info('Testando startup')

    return app
