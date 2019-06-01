from app import App, mongo
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import Usuario
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash
from datetime import datetime


@App.route('/')
@App.route('/index')
@login_required
def index():
    user = {'username': 'Gabriel'}

    posts = [
        {
            'author': {'username': 'John'},
            'body': 'The Avengers movie as so cool'},
        {'author': {'username': 'Susan'},
         'body': 'The Avengers movie as so cool'
         }
    ]

    return render_template('index.html', title='Home', posts=posts)


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

        mongo.db.usuario.insert_one({"_id": nome_usuario, "email": email, "pwhash": pwhash})
        flash("Registro bem sucedido!")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@App.route('/user/<username>')
@login_required
def user(username):
    user = Usuario(mongo.db.usuario.find_one_or_404({"_id": username}))
    posts = [
        {'author': user, 'body': 'Test post 1'},
        {'author': user, 'body': 'Test post 2'}
    ]
    return render_template('user.html', user=user, posts=posts)


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
