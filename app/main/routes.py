from app import App, mongo
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from app.main.forms import EditProfileForm, PostForm

from app.models import Usuario, Post
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash
from datetime import datetime
from app.db import get_post_objects, paginate
from app.email import send_password_reset_email
from app.main import bp


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        last_seen = datetime.utcnow()
        mongo.db.usuario.update_one({"_id": current_user.id}, {"$set": {"last_seen": last_seen}}, upsert=True)


@bp.route('/', methods=["GET", "POST"])
@bp.route('/index', methods=["GET", "POST"])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():

        mongo.db.post.insert_one({"body": form.post.data, "author": current_user.id})
        flash("Seu post é um sucesso!")
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    next_page = page + 1
    prev_page = page - 1
    if prev_page < 1:
        prev_page = 1

    cursor = paginate(current_user.id, page, current_app.config['POSTS_PER_PAGE'])
    posts = get_post_objects(cursor)

    next_url = None
    if len(posts) == current_app.config['POSTS_PER_PAGE']:
        next_url = url_for('main.index', page=next_page)
    else:
        None

    prev_url = url_for('main.index', page=prev_page)

    return render_template('index.html', title='Home', form=form, posts=posts, next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = Usuario(mongo.db.usuario.find_one_or_404({"_id": username}))
    page = request.args.get('page', 1, type=int)
    next_page = page + 1
    prev_page = page - 1

    cursor = paginate(current_user.id, page, current_app.config['POSTS_PER_PAGE'])
    posts = get_post_objects(cursor)

    next_url = url_for('main.user', username=user.id, page=next_page)
    prev_url = url_for('main.user', username=user.id, page=prev_page)
    return render_template('user.html', user=user, posts=posts, next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.id)
    if form.validate_on_submit():
        current_user.id = form.username.data
        current_user.about_me = form.about_me.data
        mongo.db.usuario.update_one({"_id": current_user.id},
                                    {"$set": {"about_me": current_user.about_me}})
        flash('As mudanças foram salvas')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.id
        try:
            form.about_me.data = current_user.about_me
        except AttributeError:
            mongo.db.usuario.update_one({"_id": current_user.id}, {"$set": {"about_me": ""}}, upsert=True)
            form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Editar perfil',
                           form=form)


