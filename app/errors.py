from flask import render_template
from app import App, mongo

@App.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@App.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

