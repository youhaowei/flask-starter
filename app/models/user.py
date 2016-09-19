from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'Visitor': (Permission.COMMENT, True),
            'Student': (Permission.STUDENT |
                        Permission.COMMENT |
                        Permission.POST, False),
            'Host': (Permission.HOST |
                     Permission.COMMENT |
                     Permission.POST, False),
            'Moderator': (Permission.COMMENT |
                          Permission.POST |
                          Permission.MODERATE_BLOG, False),
            'Administrator': (0xfff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    address = db.Column(db.String(128))
    is_family = db.Column(db.Boolean, default=False)
    profiles = db.relationship('User_Profile', backref="user", lazy="dynamic")
    email = db.Column(db.String(64), unique=True, index=True)
    permissions = db.Column(db.Integer)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_name(self):
        name = self.get_profile().get_name()
        if name:
            return name
        else:
            return self.username

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_admin(self):
        return self.can(Permission.ADMIN)

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.init_permissions()

    def get_profile(self):
        return User_Profile.query.get(int(self.id))

    def init_permissions(self):
        if self.role is None:
            if self.email == current_app.config['ADMIN_EMAIL']:
                self.role = Role.query.filter_by(permissions=0xfff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()
        self.permissions = self.role.permissions


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_admin(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def login_user(user_id):
    return User.query.get(int(user_id))


class User_Profile(db.Model):
    __tablename__ = 'user_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    is_male = db.Column(db.Boolean)
    is_single = db.Column(db.Boolean)
    is_married = db.Column(db.Boolean)

    def __init__(self, **kwargs):
        super(User_Profile, self).__init__(**kwargs)

    def get_user(self):
        return User.query.get(int(self.id))

    def get_name(self):
        # use first name if given
        if self.first_name:
            return self.first_name
        elif self.last_name:
            if self.is_male:
                return "Mr " + self.last_name
            elif self.is_male is False:
                if self.is_married:
                    return "Mrs " + self.last_name
                else:
                    return "Ms " + self.last_name
            else:
                return self.last_name
        # use username when no name info are given
        return None


class Permission:
    HOST = 0x001
    STUDENT = 0x002
    COMMENT = 0x004
    POST = 0x008
    MODERATE_MATCHING = 0x010
    MODERATE_BLOG = 0x020
    MODERATE_USER = 0x040
    BOARD_MEMBER = 0x080
    ADMIN = 0x800
