import datetime
from datetime import datetime
from app import mongo, login

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import jwt
from time import time
from app import App



class Usuario(UserMixin):

    def __init__(self, document):
        self.id = document["_id"]
        self.email = document["email"]
        self.pwhash = document["pwhash"]
        self.about_me = document["about_me"]
        self.last_seen = document["last_seen"]

    @classmethod
    def mock(cls):
        document = {"_id": 'test', "email": 'test@test.com', "pwhash": generate_password_hash('test'),
                    "about_me": 'test', "last_seen": datetime.utcnow()}

        return cls(document)




    def __repr__(self):
        return f'<Usuario {self.id}'

    @staticmethod
    def set_password(self, password):
        self.pwhash = generate_password_hash(password)


    @staticmethod
    def check_password(pwhash, password):
        return check_password_hash(pwhash, password)

    # Avatar

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'http://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    #JWT generation

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            App.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, App.config['SECRET_KEY'],
            algorithms=['HS256'])['reset_password']
        except:
            return
        return load_user(id)




class Post:

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
