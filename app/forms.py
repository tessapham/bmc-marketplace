# File: forms.py
# Author: Zainab Batool, Tessa Pham, Xinyi Wang

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateTimeField, IntegerField, TextAreaField, FloatField
from wtforms.validators import ValidationError, InputRequired, Email, EqualTo
from app.models import User
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app import images
from flask import request

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    name = StringField('Name (required)', validators=[InputRequired()])
    email = StringField ('Email (required)', validators=[InputRequired(), Email()])
    password = PasswordField('Password (required)', validators=[InputRequired()])
    password2 = PasswordField('Repeat Password', validators=[InputRequired(), EqualTo('password')])
    venmo_username = StringField('Venmo Username')
    username = StringField('Username (required)', validators=[InputRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")

class AddPostForm(FlaskForm):
    title = StringField('Title (required)', validators=[InputRequired()])
    text = TextAreaField('Item Description')
    price = FloatField('Price (required)', validators=[InputRequired()])
    submit = SubmitField('Post')

class AddCommentForm(FlaskForm):
    text = StringField('Comment', validators=[InputRequired()])
    submit = SubmitField('Post')
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[InputRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
