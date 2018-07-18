from flask import render_template, flash, redirect, url_for, request, jsonify, \
    current_app, g, abort, jsonify, session
from flask_babelex import lazy_gettext as _
from werkzeug.utils import secure_filename

from rapidannotator import db
from rapidannotator.models import User, Experiment, AnnotatorAssociation, \
    DisplayTime, AnnotationLevel, Label, TextFile, File, AnnotationInfo
from rapidannotator.modules.add_experiment import blueprint
from rapidannotator.modules.add_experiment.forms import AnnotationLevelForm
from rapidannotator import bcrypt

from flask_login import current_user, login_required
from flask_login import login_user, logout_user, current_user

from sqlalchemy import and_


import os

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
    '''
        ..  there is no need to send the all the details
            of annotator like start / end / current file
            for annotation. So just send username of the
            annotator.
    '''
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

    username = request.args.get('userName', None)
    experimentId = request.args.get('experimentId', None)

    '''do in try catch'''
    experiment = Experiment.query.filter_by(id=experimentId).first()
    user = User.query.filter_by(username=username).first()
    experiment.owners.append(user)
    db.session.commit()
    '''end try catch'''
    response = {
        'success' : True,
        'ownerId' : user.id,
        'ownerFullname' : user.fullname,
    }

    return jsonify(response)

@blueprint.route('/_addAnnotator', methods=['GET','POST'])
def _addAnnotator():

    username = request.args.get('userName', None)
    experimentId = request.args.get('experimentId', None)

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
        'annotatorId' : user.id,
        'annotatorFullname' : user.fullname,
    }

    return jsonify(response)


@blueprint.route('/labels/<int:experimentId>')
def editLables(experimentId):

    experiment = Experiment.query.filter_by(id=experimentId).first()
    annotation_levels = experiment.annotation_levels
    annotationLevelForm = AnnotationLevelForm(experimentId = experimentId)

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
        levelNumberValidated = True

        levelNumber = annotationLevelForm.levelNumber.data
        if levelNumber:
            existing = AnnotationLevel.query.filter(and_\
                        (AnnotationLevel.experiment_id==experimentId, \
                        AnnotationLevel.level_number==levelNumber)).first()
            if existing is not None:
                annotationLevelForm.levelNumber.errors.append('Level Number already used')
                levelNumberValidated = False

        if levelNumberValidated:
            annotationLevel = AnnotationLevel(
                name = annotationLevelForm.name.data,
                description = annotationLevelForm.description.data,
            )
            if levelNumber:
                annotationLevel.level_number = annotationLevelForm.levelNumber.data
            experiment.annotation_levels.append(annotationLevel)
            db.session.commit()
            return redirect(url_for('add_experiment.editLables', experimentId = experimentId))

    errors = "annotationLevelErrors"

    return render_template('add_experiment/labels.html',
        experiment = experiment,
        annotation_levels = annotation_levels,
        annotationLevelForm = annotationLevelForm,
        errors = errors,
    )

''' TODO DONE no 2 labels should have same keybinding '''
''' TODO DONE no 2 levels should have same number '''
''' TODO display level as per number '''
@blueprint.route('/_addLabels', methods=['POST','GET'])
def _addLabels():

    annotationId = request.args.get('annotationId', None)
    labelName = request.args.get('labelName', None)
    labelKey = request.args.get('labelKey', None)

    annotationLevel = AnnotationLevel.query.filter_by(id=annotationId).first()
    annotationLabels = Label.query.filter_by(annotation_id=annotationId).all()

    for label in annotationLabels:
        if labelName == label.name:
            response = {
                'error' : 'Name already taken',
            }
            return jsonify(response)
        if labelKey and (labelKey == label.key_binding):
            response = {
                'error' : 'Key already taken',
            }
            return jsonify(response)

    label = Label(
        name = labelName,
        key_binding = labelKey,
    )
    annotationLevel.labels.append(label)

    db.session.commit()
    labelId = label.id

    response = {
        'success' : True,
        'labelId' : labelId,
    }

    return jsonify(response)

@blueprint.route('/_deleteLabel', methods=['POST','GET'])
def _deleteLabel():

    labelId = request.args.get('labelId', None)
    Label.query.filter_by(id=labelId).delete()

    db.session.commit()
    response = {
        'success' : True,
    }

    return jsonify(response)

@blueprint.route('/_deleteAnnotationLevel', methods=['POST','GET'])
def _deleteAnnotationLevel():

    annotationId = request.args.get('annotationId', None)
    AnnotationLevel.query.filter_by(id=annotationId).delete()

    db.session.commit()
    response = {
        'success' : True,
    }

    return jsonify(response)

@blueprint.route('/_editAnnotationLevel', methods=['POST','GET'])
def _editAnnotationLevel():

    annotationId = request.args.get('annotationId', None)
    annotationLevel = AnnotationLevel.query.filter_by(id=annotationId).first()

    annotationLevel.name = request.args.get('annotationName', None)
    annotationLevel.description = request.args.get('annotationDescription', None)
    annotationLevel.level_number = request.args.get('annotationLevelNumber', None)

    db.session.commit()
    response = {
        'success' : True,
    }

    return jsonify(response)

@blueprint.route('/_editLabel', methods=['POST','GET'])
def _editLabel():

    labelId = request.args.get('labelId', None)
    label = Label.query.filter_by(id=labelId).first()

    label.name = request.args.get('labelName', None)
    label.key_binding = request.args.get('labelKey', None)

    db.session.commit()
    response = {
        'success' : True,
    }

    return jsonify(response)

'''
    TODO
    .. extract all text from the text file and store in database
    .. check for the allowed filename
    .. delete from folder too
'''


@blueprint.route('/_uploadFiles', methods=['POST','GET'])
def _uploadFiles():
    from rapidannotator import app

    import sys
    app.logger.info("inFunc")
    app.logger.info(request.form)
    app.logger.info(request.data)

    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return response
        ''' also check for the allowed filename '''
        if file:
            filename = secure_filename(file.filename)
            filePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filePath)
            experimentId = request.form.get('experimentId', None)
            fileCaption = request.form.get('fileCaption', None)

            experiment = Experiment.query.filter_by(id=experimentId).first()
            if experiment.category == 'text':
                pass
            else:
                newFile = File(
                    url=filename,
                )
                experiment.files.append(newFile)

            newFile.caption = fileCaption
            db.session.commit()


            response = {
            'success' : True,
            'fileId' : newFile.id,
            'fileUrl' : newFile.url,
            }

            return jsonify(response)

    response = "greatNahiHai"

    return jsonify(response)

''' delete from folder too '''
@blueprint.route('/_deleteFile', methods=['POST','GET'])
def _deleteFile():

    experimentCategory = request.args.get('experimentCategory', None)
    fileId = request.args.get('fileId', None)

    if experimentCategory == 'text':
        TextFile.query.filter_by(id=fileId).delete()
    else:
        File.query.filter_by(id=fileId).delete()

    db.session.commit()
    response = {
        'success' : True,
    }


    return jsonify(response)

@blueprint.route('/_updateFileCaption', methods=['POST','GET'])
def _updateFileCaption():

    experimentCategory = request.args.get('experimentCategory', None)
    fileId = request.args.get('fileId', None)

    if experimentCategory == 'text':
        currentFile = TextFile.query.filter_by(id=fileId).first()
    else:
        currentFile = File.query.filter_by(id=fileId).first()

    currentFile.caption = request.args.get('caption', None)

    db.session.commit()
    response = {
        'success' : True,
    }

    return jsonify(response)

@blueprint.route('/viewSettings/<int:experimentId>')
def viewSettings(experimentId):

    users = User.query.all()
    experiment = Experiment.query.filter_by(id=experimentId).first()
    owners = experiment.owners
    ''' send all the details of each annotator. '''
    annotatorDetails = experiment.annotators
    annotators = [assoc.annotator for assoc in annotatorDetails]

    notOwners = [x for x in users if x not in owners]
    notAnnotators = [x for x in users if x not in annotators]

    if experiment.category == 'text':
        pass
    else:
        totalFiles = experiment.files.count()

    return render_template('add_experiment/settings.html',
        users = users,
        experiment = experiment,
        owners = owners,
        notOwners = notOwners,
        notAnnotators = notAnnotators,
        annotatorDetails = annotatorDetails,
        totalFiles = totalFiles,
    )

@blueprint.route('/_deleteAnnotator', methods=['POST','GET'])
def _deleteAnnotator():

    annotatorId = request.args.get('annotatorId', None)
    experimentId = request.args.get('experimentId', None)

    experimentAnnotator = AnnotatorAssociation.query.filter_by(
                            experiment_id = experimentId,
                            user_id = annotatorId)
    experimentAnnotator.delete()

    db.session.commit()

    response = {
        'success' : True,
    }

    return jsonify(response)

@blueprint.route('/_editAnnotator', methods=['POST','GET'])
def _editAnnotator():

    import sys
    from rapidannotator import app
    app.logger.info("hoollllllllll")

    annotatorId = request.args.get('annotatorId', None)
    experimentId = request.args.get('experimentId', None)
    annotatorDetails = AnnotatorAssociation.query.filter_by(
                        experiment_id=experimentId,
                        user_id=annotatorId).first()

    annotatorDetails.start = request.args.get('start', annotatorDetails.start)
    annotatorDetails.end = request.args.get('end', annotatorDetails.end)

    db.session.commit()
    response = {
        'success' : True,
    }

    return jsonify(response)

@blueprint.route('/_deleteOwner', methods=['POST','GET'])
def _deleteOwner():

    ownerId = request.args.get('ownerId', None)
    experimentId = request.args.get('experimentId', None)
    user = User.query.filter_by(id=ownerId).first()
    experiment = Experiment.query.filter_by(id=experimentId).first()
    experiment.owners.remove(user)

    db.session.commit()

    response = {
        'success' : True,
    }

    return jsonify(response)


@blueprint.route('/_deleteExperiment', methods=['POST','GET'])
def _deleteExperiment():

    experimentId = request.args.get('experimentId', None)
    experiment = Experiment.query.filter_by(id=experimentId).first()
    experiment.owners = []
    db.session.delete(experiment)
    db.session.commit()


    response = {
        'success' : True,
    }

    return jsonify(response)


@blueprint.route('/viewResults/<int:experimentId>')
def viewResults(experimentId):

    users = User.query.all()
    experiment = Experiment.query.filter_by(id=experimentId).first()

    if experiment.category == 'text':
        pass
    else:
        totalFiles = experiment.files.count()

    import sys
    from rapidannotator import app
    app.logger.info("vvvvvvvvvvvvvvvvvv vvvvvvvvvvvvvvvv")
    annotations = {}

    ''' TODO take care of text_files and files '''
    for f in experiment.files:
        annotation = {}
        fileAnnotations = AnnotationInfo.query.filter_by(file_id=f.id).all()
        for fileAnnotation in fileAnnotations:
            levelId = fileAnnotation.annotationLevel_id
            labelId = fileAnnotation.label_id
            if levelId in annotation:
                annotation[levelId][labelId] = annotation[levelId].get(labelId, 0) + 1
            else:
                annotation[levelId] = {}
                annotation[levelId][labelId] = 1
        annotations[f.id] = annotation

    return render_template('add_experiment/results.html',
        users = users,
        experiment = experiment,
        totalFiles = totalFiles,
        annotations = annotations,
    )

@blueprint.route('/_discardAnnotations', methods=['POST','GET'])
def _discardAnnotations():

    experimentId = request.args.get('experimentId', None)
    annotationLevels = AnnotationLevel.query.filter_by(experiment_id=experimentId).all()

    '''
        ..  delete all the AnnotationInfo for all the levels
            of this experiment.
        ..  reset the current pointer to start pointer of the
            annotation.
    '''
    for level in annotationLevels:
        AnnotationInfo.query.filter_by(annotationLevel_id=level.id).delete()

    annotatorsInfo = AnnotatorAssociation.query.filter_by(experiment_id=experimentId).all()
    for annotatorInfo in annotatorsInfo:
        annotatorInfo.current = annotatorInfo.start

    db.session.commit()
    response = {
        'success' : True,
    }

    return jsonify(response)
