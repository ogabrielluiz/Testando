from flask import Flask
from config import Config
from flask_pymongo import PyMongo
from flask_login import LoginManager



App = Flask(__name__)
App.config.from_object(Config)
mongo = PyMongo(App)

login = LoginManager(App)
login.login_view = 'login'

from app import routes, models