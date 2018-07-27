from flask import render_template, flash, redirect, url_for, request, jsonify, \
    current_app, g
from flask_babelex import lazy_gettext as _
from flask_login import current_user, login_required, login_user, logout_user

from rapidannotator import db
from rapidannotator.models import User, RightsRequest
from rapidannotator.modules.admin import blueprint

@blueprint.before_request
def before_request():
    if current_app.login_manager._login_disabled:
        pass
    elif not current_user.is_authenticated:
        return "Please login to access this page."
    elif not current_user.is_admin():
        return "You are not an admin, hence allowed to access this page."

@blueprint.route('/')
def index():
    requests = RightsRequest.query.all()

    from rapidannotator import app
    for r in requests:
        app.logger.info(r.id)

    return render_template('admin/main.html',
        requests = requests,
        )

@blueprint.route('/toggleRequest')
def toggleRequest():

    requestId = request.args.get('requestId', None)
    req = RightsRequest.query.filter_by(id=requestId).first()
    user = User.query.filter_by(id=req.user_id).first()

    action = 0 if req.approved else 1

    if req.role == "experimenter": user.experimenter = action
    if req.role == "admin": user.admin = action
    req.approved = action

    db.session.commit()

    response = {}
    response['success'] = True

    return jsonify(response)
