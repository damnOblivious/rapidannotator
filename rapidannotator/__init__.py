from flask import Flask
app = Flask(__name__)
app.config.from_object('rapidannotator.config.DevelopmentConfig')

from flask_login import LoginManager
login = LoginManager()
login.login_view = 'frontpage.index'
login.init_app(app)

from rapidannotator.models import db
db.init_app(app)
'''
    .. for creating all the required tables
'''
with app.app_context():
    db.create_all()

from rapidannotator.modifyJsonEncoder import JSONEncoder
app.json_encoder = JSONEncoder

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

from rapidannotator.filters import datetimeformat
app.jinja_env.filters['datetimeformat'] = datetimeformat

'''
    ..import all the blueprints
'''
from rapidannotator.modules.frontpage import blueprint as frontpage
app.register_blueprint(frontpage, url_prefix='/frontpage')

from rapidannotator.modules.home import blueprint as home
app.register_blueprint(home, url_prefix='/home')

from rapidannotator.modules.add_experiment import blueprint as add_experiment
app.register_blueprint(add_experiment, url_prefix='/add_experiment')

from rapidannotator.modules.annotate_experiment import blueprint as annotate_experiment
app.register_blueprint(annotate_experiment, url_prefix='/annotate_experiment')

from rapidannotator.modules.admin import blueprint as admin
app.register_blueprint(admin, url_prefix='/admin')
