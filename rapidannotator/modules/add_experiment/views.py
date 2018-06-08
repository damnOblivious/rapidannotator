from flask import render_template, flash, redirect, url_for, request, jsonify, \
    current_app, g, abort, jsonify, session
from flask_babelex import lazy_gettext as _

from rapidannotator import db
from rapidannotator.models import User, Experiment, AnnotatorAssociation, \
    DisplayTime
from rapidannotator.modules.add_experiment import blueprint
from rapidannotator.modules.add_experiment.forms import AnnotationLevelForm
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

    return render_template('add_experiment/main.html',
        users = users,
        experiment = experiment,
        notOwners = notOwners,
        notAnnotators = notAnnotators,
    )

@blueprint.route('/_addDisplayTimeDetails', methods=['GET','POST'])
def _addDisplayTimeDetails():

    beforeTime = request.args.get('beforeTime', None)
    afterTime = request.args.get('afterTime', None)
    experimentId = request.args.get('experimentId', None)

    '''do in try catch'''
    experiment = Experiment.query.filter_by(id=experimentId).first()
    experiment.display_time = DisplayTime(
        before_time = beforeTime,
        after_time = afterTime,
    )
    '''end try catch'''
    db.session.commit()
    response = {
        'success' : True,
    }

    return jsonify(response)


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


@blueprint.route('/lables/<int:experimentId>')
def editLables(experimentId):

    experiment = Experiment.query.filter_by(id=experimentId).first()
    annotation_levels = experiment.annotation_levels
    annotationLevelForm = AnnotationLevelForm(experimentId = experimentId)

    import sys
    from rapidannotator import app
    app.logger.info("heri fera")
    app.logger.info(annotation_levels)

    return render_template('add_experiment/labels.html',
        experiment = experiment,
        annotation_levels = annotation_levels,
        annotationLevelForm = annotationLevelForm,
    )

@blueprint.route('/_addAnnotationLevel', methods=['POST'])
def _addAnnotationLevel():

    annotationLevelForm = AnnotationLevelForm()

    experimentId = annotationLevelForm.experimentId.data
    experiment = Experiment.query.filter_by(id=experimentId).first()
    annotation_levels = experiment.annotation_levels

    if annotationLevelForm.validate_on_submit():
        flash(_('Successfully added the annotation level.'))
        return redirect(url_for('add_experiment.editLables', experimentId = experimentId))

    errors = "annotationLevelErrors"

    return render_template('add_experiment/labels.html',
        experiment = experiment,
        annotation_levels = annotation_levels,
        annotationLevelForm = annotationLevelForm,
        errors = errors,
    )
