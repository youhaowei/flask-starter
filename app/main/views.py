from flask import render_template, session, current_app, abort
from . import main
from .forms import NameForm
from .. import flash
from flask_babel import gettext as _
from flask_sqlalchemy import get_debug_queries
from app.models.user import User


import configparser


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['SLOW_DB_QUERY_TIME']:
            s = 'Slow query: %s\nParameters: %s\n' % (
                query.statement, query.parameters)
            s += 'Duration: %f sec\nContext: %s\n' % (
                query.duration, query.context)
            current_app.logger.warning(s)
    return response


@main.route('/', methods=['GET', 'POST'])
def index():
    config = configparser.RawConfigParser()
    config.read("settings/index.cfg")
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash(_('Looks like you have changed your name'))
        session['name'] = form.name.data
    form.name.data = ''

    setting = {
        "COUNT": int(config.get('INDEX', 'CAROUSEL_SLIDE_COUNT')),
        "SOURCES": config.get("INDEX", "CAROUSEL_IMG_SOURCES").split(','),
        "CAPTIONS": config.get("INDEX", "CAROUSEL_CAPTIONS").split(',')
    }

    print(setting)

    return render_template('index.html',
                           setting=setting,
                           form=form, name=session.get('name'))


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)

    return render_template('user.html', user=user)
