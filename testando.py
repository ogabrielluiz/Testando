from app import App, mongo
from app .models import Usuario, Post
from app.db import *

@App.shell_context_processor
def make_shell_context():
    return {'mongo': mongo, 'Usuario': Usuario, 'Post': Post}