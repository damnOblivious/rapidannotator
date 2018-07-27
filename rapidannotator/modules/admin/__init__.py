from flask import Blueprint

blueprint = Blueprint(
        'admin',
        __name__,
        template_folder='templates',
)

from rapidannotator.modules.admin import views
