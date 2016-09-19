from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import ValidationError
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from wtforms.fields.html5 import EmailField
from flask_babel import gettext as _
from app.models.user import User


class LoginForm(Form):
    email_or_username = StringField(
        _('Email/Username'), validators=[Required(), Length(1, 64)])
    password = PasswordField(_('Password'), validators=[Required()])
    remember_me = BooleanField(_('Keep me logged in'))
    submit = SubmitField(_('Login'))


class RegisterForm(Form):
    email = EmailField(_('Your Email'), validators=[
                       Required(), Length(1, 64), Email()])
    username = StringField(
        _('Your Username'), validators=[Required(), Length(1, 64), Regexp(
            '^[A-Za-z0-9_.]*$',
            0,
            _("""
              Username must have only letters, numbers, dots or underscores
              """))])
    password = PasswordField(
        _('Your Password'), validators=[Required(), EqualTo(
            'password_reentery', message=_("password doesn't match"))])
    password_reentery = PasswordField(
        _("Confirm Password"), validators=[Required()])
    submit = SubmitField(_("Register"))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(
                _("The email address seems to be already registered."))

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(_("Username already taken."))
