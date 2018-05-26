from flask import render_template, flash, redirect, url_for, request, jsonify, \
    current_app, g, abort, jsonify
from flask_babelex import lazy_gettext as _

from rapidannotator import db
from rapidannotator.models import User, Experiment
from rapidannotator.modules.add_experiment import blueprint

from rapidannotator import bcrypt
from flask_login import current_user, login_required
from flask_login import login_user, logout_user, current_user

'''
@blueprint.before_request
def before_request():
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
'''

@blueprint.before_request
@login_required
def before_request():
    pass

@blueprint.route('/a/<int:experimentId>')
def index(experimentId):
    users = User.query.all()
    experiment = Experiment.query.filter_by(id=experimentId).first()

    return render_template('add_experiment/main.html',
        users = users,
        experiment = experiment,
    )

@blueprint.route('/_addExperimentOwner', methods=['GET','POST'])
def _addExperimentOwner():

    import sys
    from rapidannotator import app
    app.logger.info("heri fera")
    app.logger.info(request.args)

    response = {
        'success' : True,
    }

    return jsonify(response)
