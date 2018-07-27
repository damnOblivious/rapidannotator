from flask import render_template, flash, redirect, url_for, request, jsonify, \
    current_app, abort
from flask_babelex import lazy_gettext as _
from flask_login import current_user, login_required, login_user, logout_user

from rapidannotator import db
from rapidannotator import bcrypt
from rapidannotator.models import User, Experiment, RightsRequest
from rapidannotator.modules.home import blueprint
from rapidannotator.modules.home.forms import AddExperimentForm

@blueprint.before_request
def before_request():
    if current_app.login_manager._login_disabled:
        pass
    elif not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()



@blueprint.route('/')
def index():
    addExperimentForm = AddExperimentForm()
    myExperiments = current_user.my_experiments.all()
    annotatorAssociation = current_user.experiments_to_annotate
    experimentsToAnnotate = [association.experiment for association in annotatorAssociation]

    return render_template('home/main.html',
        addExperimentForm = addExperimentForm,
        myExperiments = myExperiments,
        experimentsToAnnotate = experimentsToAnnotate,
        )

@blueprint.route('/addExperiment', methods=['POST'])
def addExperiment():
    addExperimentForm = AddExperimentForm()

    if addExperimentForm.validate_on_submit():
        experiment = Experiment(
            name=addExperimentForm.name.data,
            description=addExperimentForm.description.data,
            category=addExperimentForm.category.data,
        )
        experiment.owners.append(current_user)
        db.session.add(experiment)
        db.session.commit()

        experimentId = experiment.id
        return redirect(url_for('add_experiment.index', experimentId = experimentId))

    errors = "addExperimentErrors"
    return render_template('home/main.html',
        addExperimentForm = addExperimentForm,
        errors = errors,)


@blueprint.route('/askRights', methods=['GET', 'POST'])
def askRights():
    message = request.args.get('message', '')
    role = request.args.get('role', 'experimenter')

    rightsRequest = RightsRequest(
        user_id = current_user.id,
        username = current_user.username,
        role = role,
        message = message,
    )

    db.session.add(rightsRequest)
    db.session.commit()

    response = {}
    response['success'] = True

    return jsonify(response)

''' check for what right do the user has / requested for '''
@blueprint.route('/checkRights', methods=['GET', 'POST'])
def checkRights():

    requestsSent = RightsRequest.query.filter_by(user_id=current_user.id)
    response = {}
    response['success'] = True

    for r in requestsSent:
        if r.role == "experimenter": response['experimenterRequest'] = True
        if r.role == "admin": response['adminRequest'] = True

    return jsonify(response)

@blueprint.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('frontpage.index'))
