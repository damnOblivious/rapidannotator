from flask import render_template, flash, redirect, url_for, request, jsonify, \
    current_app, g
from flask_babelex import lazy_gettext as _
from flask_login import current_user, login_required, login_user, logout_user

from rapidannotator import db
from rapidannotator import bcrypt
from rapidannotator.models import User
from rapidannotator.modules.frontpage import blueprint
from rapidannotator.modules.frontpage.forms import LoginForm, RegistrationForm

@blueprint.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    loginForm = LoginForm()
    registrationForm = RegistrationForm()
    return render_template('frontpage/main.html',
        loginForm = loginForm,
        registrationForm = registrationForm)

@blueprint.route('/login', methods=['POST'])
def login():
    loginForm = LoginForm()
    registrationForm = RegistrationForm()

    if loginForm.validate_on_submit():
        user = User.query.filter_by(username=loginForm.username.data).first()
        if user is None or not bcrypt.check_password_hash(
                                user.password, loginForm.password.data):
            flash(_('Invalid username or password'))
            return render_template('frontpage/main.html',
                loginForm = loginForm,
                registrationForm = registrationForm)

        login_user(user, remember=loginForm.remember_me.data)
        return redirect(url_for('home.index'))

    return render_template('frontpage/main.html',
        loginForm = loginForm,
        registrationForm = registrationForm)

@blueprint.route('/register', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return "already logged in! :) :) "
    loginForm = LoginForm()
    registrationForm = RegistrationForm()

    if registrationForm.validate_on_submit():
        hashedPassword = bcrypt.generate_password_hash(
            registrationForm.password.data).decode('utf-8')

        user = User(
            username=registrationForm.username.data,
            fullname=registrationForm.fullname.data,
            email=registrationForm.email.data,
            password=hashedPassword
        )
        db.session.add(user)
        db.session.commit()

        flash(_('Thank you, you are now a registered user.'))
        flash(_('Please Login to continue.'))

        return render_template('frontpage/main.html',
            loginForm = loginForm,
            registrationForm = registrationForm)

    return render_template('frontpage/main.html',
        loginForm = loginForm,
        registrationForm = registrationForm)
