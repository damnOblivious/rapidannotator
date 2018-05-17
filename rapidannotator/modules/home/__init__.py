from flask import Blueprint

blueprint = Blueprint(
        'home',
        __name__,
        template_folder='templates',
)

from rapidannotator.modules.home import views
