# Authors: Tessa Pham, Zainab Batool, Xinyi Wang

from app import app, db
from app.models import User, Post, Interested

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'interested': Interested}
