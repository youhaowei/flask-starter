from flask import render_template, redirect, request, url_for
from ..email import send_email
from app import flash, db
from flask_login import (
    login_user, login_required, logout_user, current_user
)
from . import auth
from app.models.user import User, User_Profile
from .forms import LoginForm, RegisterForm
from flask_babel import gettext as _


@auth.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email_or_username.data).first()
        if user is None:
            user = User.query.filter_by(
                username=form.email_or_username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(_('Invalid user name or password'), 'd')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 's')
    return redirect(request.args.get('next') or url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data,
                    password=form.password.data)
        profile = User_Profile(id=user.id)
        db.session.add(user)
        db.session.add(profile)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash(_("A confirmation email has been sent to you by email."), "s")
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash(_("You have confirmed your account. Thanks!"), 's')
    else:
        flash(
            _("The confirmation link is invalid or has expired." +
              "click <a href='{{url_for('auth.resend_confirmation'}}'>" +
                "here</a>" +
              "to resend the link"), 'd')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, "Confirm Your Account",
               'auth/email/confirm', user=current_user, token=token)
    flash(_("A confirmation email has been sent to you by email."), "s")
    return redirect(request.args.get('next') or url_for('main.index'))
