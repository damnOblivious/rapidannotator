from flask import render_template, flash, redirect, url_for, request, jsonify, \
    current_app, g
from flask_babelex import lazy_gettext as _

from rapidannotator import db
from rapidannotator.models import User
from rapidannotator.modules.home import blueprint

from rapidannotator import bcrypt
from flask_login import current_user, login_required
from flask_login import login_user, logout_user, current_user

@blueprint.route('/')
def index():
    return render_template('home/main.html')

@blueprint.route('/logout', methods=['GET','POST'])
def logout():
    logout_user()
    return redirect(url_for('frontpage.index'))
