from flask import Flask
from config import Config
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os



App = Flask(__name__)
App.config.from_object(Config)
mongo = PyMongo(App)
mail = Mail(App)
bootstrap = Bootstrap(App)

login = LoginManager(App)
login.login_view = 'login'

from app import routes, models, errors

if not App.debug:
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
