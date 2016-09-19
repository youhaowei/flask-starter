from flask import Flask
from flask import flash as f
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_babel import Babel
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_wtf.csrf import CsrfProtect
from config import configs

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
db = SQLAlchemy()
bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
babel = Babel()
pagedown = PageDown()
csrf = CsrfProtect()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(configs[config_name])
    configs[config_name].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    babel.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    csrf.init_app(app)

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    return app

# global functions


def flash(message="", flag=False):
    if flag:
        f(flag + '/' + message)
    else:
        f(message)
