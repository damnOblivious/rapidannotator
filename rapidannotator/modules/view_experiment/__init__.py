from flask import Blueprint

blueprint = Blueprint(
        'view_experiment',
        __name__,
        template_folder='templates',
)

from rapidannotator.modules.view_experiment import views
