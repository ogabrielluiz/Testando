import datetime
from app import mongo, login

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from bson.objectid import ObjectId


class Usuario(UserMixin):

    def __init__(self, username):
        self.id = username

    def __repr__(self):
        return f'<Usuario {self.username}'

    @staticmethod
    def check_password(pwhash, password):
        return check_password_hash(pwhash, password)






class Post():

    def __init__(self, body, author):
        self.body = body
        self.author = author

    def __repr__(self):
        return f'<Post {self.body}>'


@login.user_loader
def load_user(username):
    u = mongo.db.usuario.find_one({"_id": username})
    if not u:
        return None
    return Usuario(u['_id'])
