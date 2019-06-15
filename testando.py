from app import create_app, mongo
from app.models import Usuario, Post
from app.db import *

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'mongo': mongo, 'Usuario': Usuario, 'Post': Post}