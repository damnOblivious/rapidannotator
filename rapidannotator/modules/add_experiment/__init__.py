from flask import Blueprint

blueprint = Blueprint(
        'add_experiment',
        __name__,
        template_folder='templates',
)

from rapidannotator.modules.add_experiment import views
