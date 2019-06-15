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
from app.auth import bp


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        query = mongo.db.usuario.find_one({"_id": form.username.data})
        try:
            u = Usuario(query)
        except TypeError as _:
            flash("Invalid username or password")
            return redirect(url_for('login'))

        if u is None or not u.check_password(u.pwhash, form.password.data):
            flash("Invalid username or password")
            return redirect(url_for('login'))

        login_user(u, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@bp.route('/register', methods=['GET', 'POST'])
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




@bp.route('/reset_password_request', methods=['GET','POST'])
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

@bp.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = Usuario.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        mongo.db.usuario.update_one({"_id": current_user.id}, {"$set": {"pwhash": user.pwhash}})
        flash("Your password has been reset.")
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
