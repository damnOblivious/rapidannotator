from flask import Blueprint

blueprint = Blueprint(
        'annotate_experiment',
        __name__,
        template_folder='templates',
)

from rapidannotator.modules.annotate_experiment import views
