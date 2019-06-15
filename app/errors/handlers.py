from flask import render_template
from app import App, mongo
from app.errors import bp


@bp.App.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@bp.App.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

