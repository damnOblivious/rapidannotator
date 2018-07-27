"""Forms for Login/Registeration."""

from flask_wtf import FlaskForm
from flask_login import current_user
from flask_babelex import lazy_gettext as _
from sqlalchemy.orm.exc import NoResultFound
from flask_security.forms import email_required, email_validator, \
    unique_user_email
from wtforms import FormField, PasswordField, StringField, SubmitField, \
    BooleanField
from wtforms.validators import DataRequired, EqualTo, StopValidation, \
    ValidationError, Email

from rapidannotator.models import User
from rapidannotator.validators import USERNAME_RULES, validate_username

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
