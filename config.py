import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MONGO_URI = "mongodb://localhost:27017/testando"

    #Email
    MAIL_SERVER = 'debugmail.io'
    MAIL_PORT = 25
    MAIL_USERNAME = 'gabrielf.almeida90@gmail.com'
    MAIL_PASSWORD = '3ac445a0-865e-11e9-8b65-7d073a390350'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    ADMINS = ['gabrielf.almeida90@gmail.com']

    #Pagination
    POSTS_PER_PAGE = 25


