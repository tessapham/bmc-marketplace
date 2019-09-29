# File: models.py
# Author: Tessa Pham, Xinyi Wang
# Stores database models.

from app import db, login, app
from time import time
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(250))
    email = db.Column(db.String(250), nullable=False)
    venmo = db.Column(db.String(25))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    interested = db.relationship('Interested', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def __repr__(self):
        return "<User(username='%s', name='%s', email='%s')>" % (self.username, self.name, self.email)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_posts(self):
        return self.posts

    def show_interest(self, post):
        interest = Interested(user_id=self.id, post_id=post.id)
        db.session.add(interest)

    def unshow_interest(self, post):
        Interested.query.filter_by(user_id=self.id, post_id=post.id).delete()

    def has_interest(self, post):
        return Interested.query.filter(Interested.user_id == self.id, Interested.post_id == post.id).count() > 0

    def get_interested_posts(self):
        p = User.query.filter_by(id=self.id).first()
        results = p.interested
        list_posts = []
        for result in results:
            post_ID = result.post_id
            if not post_ID:
                continue
            post = Post.query.get(int(post_ID))
            list_posts.append(post)
        return list_posts
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Post(db.Model):
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    sold = db.Column(db.Boolean, default = False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # photos = db.Column(db.ARRAY(db.String))
    image_filenames = db.Column(db.String, default=None, nullable=True)
    image_urls = db.Column(db.String, default=None, nullable=True)
    interested = db.relationship('Interested', backref='post', lazy='dynamic')
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def __repr__(self):
        return "<Post(id='%s', user_id='%s', text='%s', timestamp='%s')>" % (self.id, self.user_id, self.text, self.timestamp)

    def get_id(self):
        return self.id

    def if_sold(self):
        return self.sold

    def mark_sold(self):
        self.sold = True

    def unmark_sold(self):
        self.sold = False

    def count_interested(self):
        p = Post.query.filter_by(id=self.id).first()
        return p.interested.count()

    def get_interested_members(self):
        p = Post.query.filter_by(id=self.id).first()
        results = p.interested
        list_buyers = []
        for result in results:
            user_ID = result.user_id
            user = User.query.get(int(user_ID))
            list_buyers.append(user.username)
        return ', '.join(list(dict.fromkeys(list_buyers)))
    
    def get_comments(self):
        return Comment.query.filter_by(post_id=self.id)

    def has_comment(self):
        return self.count_comments() > 0
    
    def count_comments(self):
        return Comment.query.filter_by(post_id=self.id).count()

class Interested(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return "<Comment(id='%s', user_id='%s', text='%s', timestamp='%s')>" % (self.id, self.user_id, self.text, self.timestamp)
    
    def get_id(self):
        self.id

def get_all_posts():
    if not Post.__table__.exists(db.engine):
        Post.__table__.create(db.engine)
    all_posts = Post.query.all()
    return all_posts

@login.user_loader
def load_user(id):
    return User.query.get(int(id))