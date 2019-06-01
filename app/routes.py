from app import App, mongo
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm
from app.models import Usuario
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash


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

        u = mongo.db.usuario.find_one({"_id": form.username.data})
        user = Usuario(u['_id'])
        pwhash = u['pwhash']


        if user is None or not user.check_password(pwhash,form.password.data):
            flash("Invalid username or password")
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
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
