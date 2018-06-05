"""Forms for Login/Registeration."""

from flask_babelex import lazy_gettext as _
from flask_login import current_user
from flask_security.forms import email_required, email_validator, \
    unique_user_email
from flask_wtf import FlaskForm
from sqlalchemy.orm.exc import NoResultFound
from wtforms import FormField, PasswordField, StringField, SubmitField, \
    BooleanField, SelectField
from wtforms.validators import DataRequired, EqualTo, StopValidation, \
    ValidationError, Email, Length

from rapidannotator.models import Experiment


def strip_filter(text):
    """Filter for trimming whitespace.

    :param text: The text to strip.
    :returns: The stripped text.
    """
    return text.strip() if text else text

class AddExperimentForm(FlaskForm):
    name = StringField(
        label=_('Experiment Name'),
        description=_("Required. Experiment name can't exceed 40 characters"),
        validators=[DataRequired(message=_('Experiment name not provided.')),
                    Length(max=40 ,message=_("Experiment name can't exceed 40 characters."))],
        filters=[strip_filter],
    )

    description = StringField(
        label=_('Experiment description'),
        description=_("A short description, can't exceed 320 characters"),
        validators=[Length(max=320 ,message=_("Experiment description can't exceed 320 characters."))],
        filters =[strip_filter],
    )

    category = SelectField(
        label=_('Type of experiment'),
        description=_("Select the type of files that your experiment has."),
        choices=[   ('text', 'text'),
                    ('image', 'image'),
                    ('audio', 'audio'),
                    ('video', 'video')],
    )
    def validate_name(self, name):
        experiment = Experiment.query.filter_by(name=name.data).first()
        if experiment is not None:
            raise ValidationError(_('Experiment name already taken!'))

class DummyForm(FlaskForm):
    """A Dummy form for testing and debugging."""

    username = StringField(_('Enter something random'),)
    submit = SubmitField(_('Sign In'))

class DummyForm2(FlaskForm):
    """A Dummy form for testing and debugging."""

    username = StringField(_('Enter something random From 2'),)
    email = StringField(_('Email'),)
    password = PasswordField(_('Password'),)
    submit = SubmitField(_('Sign In'))
