from flask import render_template, flash, redirect, url_for, request, jsonify, \
    current_app, g, abort
from flask_babelex import lazy_gettext as _
from flask_login import current_user, login_required, login_user, logout_user

from rapidannotator import db
from rapidannotator import bcrypt
from rapidannotator.models import User, Experiment
from rapidannotator.modules.home import blueprint
from rapidannotator.modules.home.forms import AddExperimentForm

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


@blueprint.route('/')
def index():
    addExperimentForm = AddExperimentForm()
    myExperiments = current_user.my_experiments.all()
    return render_template('home/main.html',
        addExperimentForm = addExperimentForm,
        myExperiments = myExperiments,
        )

@blueprint.route('/addExperiment', methods=['POST'])
def addExperiment():
    addExperimentForm = AddExperimentForm()
    addExperimentErrors = "errors"

    if addExperimentForm.validate_on_submit():
        addExperimentErrors = ""
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

    return render_template('home/main.html',
        addExperimentForm = addExperimentForm,
        addExperimentErrors = addExperimentErrors,)


@blueprint.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('frontpage.index'))
