# Authors: Zainab Batool, Tessa Pham, Xinyi Wang, Elia Anagnostou

import os
from flask import render_template, url_for, redirect, flash, request, Flask, send_from_directory, current_app
from app import app, db
from time import time
from app.forms import LoginForm, RegisterForm, AddPostForm, ResetPasswordRequestForm, SearchForm, ResetPasswordForm, AddCommentForm
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User, Post, get_all_posts, Interested, Comment
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from datetime import datetime
from flask import g
from flask_babel import get_locale
from app.email import send_password_reset_email

ALLOWED_EXTENSIONS = set(['png','jpg','jpeg'])

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    posts = get_all_posts()
    form = AddPostForm()
    comment_form = AddCommentForm()

    if request.method == 'POST' and form.validate_on_submit():
        # check if the post request has the image part
        if 'images' not in request.files:
            flash("No image provided!", "error")
            return redirect(request.url)

        file_list = request.files.getlist('images')
        filenames = ''
        urls = ''

        for file in file_list:
            if file.filename == '':
                flash("No selected file.", "error")
                return redirect(request.url)

            if not file:
                flash("File is empty!", "error")
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                url = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
                file.save(url)
            else:
                filename = ''
                url = ''

            filenames += ';%s' % filename
            urls += ';%s' % url
        filenames = filenames[1:]
        urls = urls[1:]
        post = Post(title=form.title.data, text=form.text.data, price=form.price.data, timestamp=datetime.utcnow(), user_id=current_user.get_id(), image_filenames=filenames, image_urls=urls)
        db.session.add(post)
        db.session.commit()
        flash("Item posted!", "success")
        return redirect(url_for('index'))

    return render_template('index.html', title='Home', posts=posts, form=form, comment_form=comment_form)

def allowed_file(filename):
    return '.'in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash("Invalid username or password.", "error")
                return redirect(url_for('login'))
            login_user(user, remember=form.remember_me.data)
            flash("You were logged in", "success")
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template('login.html', title='Log In', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.get_posts()
    interests = user.get_interested_posts()
    return render_template('user.html', title='User Profile', user=user, posts=posts, interests=interests)

@app.route('/post/<id>')
@login_required
def post(id):
    post = Post.query.filter_by(id=id).first_or_404()
    comments = post.get_comments()
    comment_form = AddCommentForm()
    return render_template('individual_post.html', title='Post', post=post, comments=comments, comment_form=comment_form)

@app.route('/delete/<post_id>', methods=['GET', 'POST'])
def delete_post(post_id):
    post = Post.query.get(int(post_id))
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted!", "success")
    return redirect(url_for('user', username=current_user.username))

@app.route('/logout')
def logout():
    logout_user()
    flash("You were logged out", "success")
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, name=form.name.data, email=form.email.data, venmo=form.venmo_username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!", "success")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/post/<int:post_id>/<action>', methods = ['GET','POST'])
@login_required
def interested(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'show_interest':
        current_user.show_interest(post)
        db.session.commit()
    if action == 'unshow_interest':
        current_user.unshow_interest(post)
        db.session.commit()
    return redirect(request.referrer)


@app.route('/soldpost/<int:post_id>/<action>', methods = ['GET','POST'])
@login_required
def sold(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action =='unmark_sold':
        setattr(post, 'sold', False)
        print("attempted unmark sold")
        db.session.commit()
    elif action =='mark_sold':
        setattr(post, 'sold', True)
        print("attempted mark sold")
        db.session.commit()
    else:
        raise Exception("Wrong!!!")
    return redirect(request.referrer)

@app.route("/post/<int:post_id>/comment", methods=["GET", "POST"])
@login_required
def comment_post(post_id):
    post = Post.query.get_or_404(post_id)
    comment_form = AddCommentForm()
    # this only gets executed when the form is submitted and not when the page loads
    if request.method == 'POST':
        if comment_form.validate_on_submit():
            comment = Comment(text=comment_form.text.data, user_id=current_user.id, post_id=post.id)
            db.session.add(comment)
            db.session.commit()
            print("Comment added to database!")
            flash("Your comment has been added to the post!", "success")
    return redirect(url_for('index'))

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash("Check your email for the instructions to reset your password", "success")
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset.", "success")
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
