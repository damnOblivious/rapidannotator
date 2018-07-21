"""Forms for Login/Registeration."""

from flask_babelex import lazy_gettext as _
from flask_login import current_user
from flask_security.forms import email_required, email_validator, \
    unique_user_email
from flask_wtf import FlaskForm
from sqlalchemy.orm.exc import NoResultFound
from wtforms import FormField, PasswordField, StringField, SubmitField, \
    BooleanField, IntegerField, HiddenField, FieldList, SelectField
from wtforms.validators import DataRequired, EqualTo, StopValidation, \
    ValidationError, Email, Length

from rapidannotator.models import User


def strip_filter(text):
    """Filter for trimming whitespace.

    :param text: The text to strip.
    :returns: The stripped text.
    """
    return text.strip() if text else text

class LabelForm(FlaskForm):

    annotationLevelId = HiddenField(
        label=_('Associated annotation level id'),
        description=_("Id of the associated annotation level"),
        validators=[DataRequired(message=_('Associated annotation level id not provided.'))],
    )

    name = StringField(
        label=_('Label Name'),
        description=_("Label Name : Example Male, Female. \
                Can't exceed 32 characters"),
        validators=[DataRequired(message=_('Label name not provided.')),
                    Length(min=1, max=32)],
        filters=[strip_filter],
    )

    keyBinding = StringField(
        label=_('Key Binding'),
        description=_("The key bound to the label."),
        validators=[Length(min=0, max=1)],
        filters =[strip_filter],
    )

    def validate_key_binding(self, key_binding):
        """
            Check if the same key is bound to any
            other label in the same annotation level.
            If key_binding == None: assign any random key
            that is not previously assigned to any other
            label in the same annotation level.
        """
        pass

class AnnotationLevelForm(FlaskForm):

    experimentId = HiddenField(
        label=_('Associated experiment id'),
        description=_("Id of the associated Experiment"),
        validators=[DataRequired(message=_('Associated experiment id not provided.'))],
    )

    name = StringField(
        label=_('Annotation Level Name'),
        description=_("Name of the annotation level: Example Gender, Age. \
                Can't exceed 32 characters"),
        validators=[DataRequired(message=_('Annotation level name not provided.')),
                    Length(min=1, max=32)],
        filters=[strip_filter],
    )

    description = StringField(
        label=_('Annotation level description'),
        description=_("A short description : guidilines for the annotator. \
                Can't exceed 640 characters"),
        validators=[Length(max=640 ,message=_("Annotation level description can't exceed 640 characters."))],
        filters =[strip_filter],
    )

    levelNumber = IntegerField(
        label=_('Annotation level Number'),
        description=_("It decides the order in which an annotator is asked to annotate the data-items."),
        validators=[DataRequired(message=_('Annotation level number not provided.'))],
    )

    def reset(self):
        blankData = MultiDict([ ('csrf', self.generate_csrf_token() ) ])
        self.process(blankData)
