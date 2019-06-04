from app import App, mongo
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm
from app.forms import ResetPasswordForm
from app.models import Usuario, Post
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash
from datetime import datetime
from app.db import get_post_objects, paginate
from app.email import send_password_reset_email


@App.route('/', methods=["GET", "POST"])
@App.route('/index', methods=["GET", "POST"])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():

        mongo.db.post.insert_one({"body": form.post.data, "author": current_user.id})
        flash("Seu post é um sucesso!")
        return redirect(url_for('index'))

    page = request.args.get('page', 1, type=int)
    next_page = page + 1
    prev_page = page - 1
    cursor = paginate(current_user.id, page, App.config['POSTS_PER_PAGE'])
    posts = get_post_objects(cursor)

    next_url = url_for('index', page= next_page)
    prev_url = url_for('index', page= prev_page)

    return render_template('index.html', title='Home', form=form, posts=posts, next_url=next_url, prev_url=prev_url)


@App.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():

        u = Usuario(mongo.db.usuario.find_one({"_id": form.username.data}))

        if u is None or not u.check_password(u.pwhash, form.password.data):
            flash("Invalid username or password")
            return redirect(url_for('login'))

        login_user(u, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@App.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@App.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        nome_usuario = form.username.data
        email = form.email.data
        pw = form.password.data
        pwhash = generate_password_hash(pw)

        mongo.db.usuario.insert_one({"_id": nome_usuario,
                                     "email": email,
                                     "pwhash": pwhash,
                                     "about_me": '',
                                     "last_seen": ''})
        flash("Registro bem sucedido!")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@App.route('/user/<username>')
@login_required
def user(username):
    user = Usuario(mongo.db.usuario.find_one_or_404({"_id": username}))
    page = request.args.get('page', 1, type=int)
    next_page = page + 1
    prev_page = page - 1

    cursor = paginate(current_user.id, page, App.config['POSTS_PER_PAGE'])
    posts = get_post_objects(cursor)

    next_url = url_for('user', username=user.id, page=next_page)
    prev_url = url_for('user', username=user.id, page=prev_page)
    return render_template('user.html', user=user, posts=posts, next_url=next_url, prev_url=prev_url)


@App.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.id)
    if form.validate_on_submit():
        current_user.id = form.username.data
        current_user.about_me = form.about_me.data
        mongo.db.usuario.update_one({"_id": current_user.id},
                                    {"$set": {"about_me": current_user.about_me}})
        flash('As mudanças foram salvas')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.id
        try:
            form.about_me.data = current_user.about_me
        except AttributeError:
            mongo.db.usuario.update_one({"_id": current_user.id}, {"$set": {"about_me": ""}}, upsert=True)
            form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Editar perfil',
                           form=form)


@App.before_request
def before_request():
    if current_user.is_authenticated:
        last_seen = datetime.utcnow()
        mongo.db.usuario.update_one({"_id": current_user.id}, {"$set": {"last_seen": last_seen}}, upsert=True)

@App.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = Usuario(mongo.db.usuario.find_one_or_404({"email": form.email.data}))
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@App.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = Usuario.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form =  ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        mongo.db.usuario.update_one({"_id": current_user.id}, {"$set": {"pwhash": user.pwhash}})
        flash("Your password has been reset.")
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
