"""Validators functions"""

from __future__ import absolute_import, print_function
import re
from flask_babelex import lazy_gettext as _

username_regex = re.compile('^[a-zA-Z][a-zA-Z0-9-_]{2}[a-zA-Z0-9-_]*$')
"""Username rules."""

USERNAME_RULES = _(
    'Username must start with a letter, at least three characters long and'
    ' only contain alphanumeric characters, dashes and underscores.')
"""Description of username validation rules.
.. note:: Used for both form help text and for form validation error."""

def validate_username(username):
    """Validate the username.

    See :data:`above.username_regex` to know which rules are applied.

    :param username: The user name.
    :raises ValueError: If validation fails.
    """
    pass
    # if not username_regex.match(username):
    #     raise ValueError(USERNAME_RULES)
