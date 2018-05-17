from flask import Blueprint

blueprint = Blueprint(
        'frontpage',
        __name__,
        template_folder='templates',
)

from rapidannotator.modules.frontpage import views
