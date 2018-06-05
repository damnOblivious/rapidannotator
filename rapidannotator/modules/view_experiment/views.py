from flask import render_template, flash, redirect, url_for, request, jsonify, \
    current_app, g, abort, jsonify, session
from flask_babelex import lazy_gettext as _

from rapidannotator import db
from rapidannotator.models import User, Experiment, AnnotatorAssociation
from rapidannotator.modules.view_experiment import blueprint

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
    owners = experiment.owners
    annotators = experiment.annotators
    annotators = [assoc.annotator for assoc in annotators]

    notOwners = [x for x in users if x not in owners]
    notAnnotators = [x for x in users if x not in annotators]

    import sys
    from rapidannotator import app
    app.logger.info("Oh ghosh")

    return render_template('view_experiment/main.html',
        users = users,
        experiment = experiment,
        notOwners = notOwners,
        notAnnotators = notAnnotators,
    )

@blueprint.route('/_addOwner', methods=['GET','POST'])
def _addOwner():

    username = request.args['userName']
    experimentId = request.args['experimentId']

    '''do in try catch'''
    experiment = Experiment.query.filter_by(id=experimentId).first()
    user = User.query.filter_by(username=username).first()
    experiment.owners.append(user)
    db.session.commit()
    '''end try catch'''
    response = {
        'success' : True,
    }

    return jsonify(response)

@blueprint.route('/_addAnnotator', methods=['GET','POST'])
def _addAnnotator():

    username = request.args['userName']
    experimentId = request.args['experimentId']

    '''do in try catch'''
    experiment = Experiment.query.filter_by(id=experimentId).first()
    user = User.query.filter_by(username=username).first()

    experimentAnnotator = AnnotatorAssociation()
    experimentAnnotator.experiment = experiment
    experimentAnnotator.annotator = user
    db.session.commit()
    '''end try catch'''

    response = {
        'success' : True,
    }

    return jsonify(response)
