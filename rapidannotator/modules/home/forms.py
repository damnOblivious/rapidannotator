"""Forms for Login/Registeration."""

from flask_babelex import lazy_gettext as _
from flask_login import current_user
from flask_security.forms import email_required, email_validator, \
    unique_user_email
from flask_wtf import FlaskForm
from sqlalchemy.orm.exc import NoResultFound
from wtforms import FormField, PasswordField, StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo, StopValidation, \
    ValidationError, Email

from rapidannotator.models import User


def strip_filter(text):
    """Filter for trimming whitespace.

    :param text: The text to strip.
    :returns: The stripped text.
    """
    return text.strip() if text else text

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
