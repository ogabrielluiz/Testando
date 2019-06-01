import datetime
from app import mongo, login

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5


class Usuario(UserMixin):

    def __init__(self, document):
        self.id = document["_id"]
        self.email = document["email"]
        self.pwhash = document["pwhash"]
        self.about_me = document["about_me"]
        self.last_seen = document["last_seen"]


    def __repr__(self):
        return f'<Usuario {self.id}'

    @staticmethod
    def check_password(pwhash, password):
        return check_password_hash(pwhash, password)

    #Avatar
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'http://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'






class Post():

    def __init__(self, body, author):
        self.body = body
        self.author = author

    def __repr__(self):
        return f'<Post {self.body}>'


@login.user_loader
def load_user(username):
    u = Usuario(mongo.db.usuario.find_one({"_id": username}))
    if not u:
        return None
    return u
