from app import create_app, db
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
import configparser
from app.models.user import *

"""
Which config mode do you want?
valid options: 'development'|'production'|'test'
"""
config = configparser.RawConfigParser()
config.read("setting.cfg")
config_name = config.get('IF', 'mode')

app = create_app(config_name)
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(
        app=app, db=db, Role=Role, User=User, User_Profile=User_Profile)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def profile(length=25, profile_dir=None):
    """start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(
        app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    """run deployment tasks"""
    from flask_migrate import upgrade
    from app.models.user import Role

    print(config_name)

    upgrade()
    Role.insert_roles()


if __name__ == '__main__':
    manager.run()
