from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import Enum, String, Integer, Boolean
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from flask_login import UserMixin
from flask_security import RoleMixin

from rapidannotator.validators import validate_username
from rapidannotator import login

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User data model."""

    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key=True)

    """Lower-case username to assert uniqueness."""
    username = db.Column(db.String(255), nullable=False, unique=True)

    """Full name of person."""
    fullname = db.Column(db.String(255), nullable=False, default='')

    """User email."""
    email = db.Column(db.String(255), nullable=False, unique=True)

    """User password."""
    password = db.Column(db.String(300))

    """ There are 3 levels of user hierarchy,
    userrole field in the User relation can be any one of
    ..  Annotator,
    ..  Experimenter,
    ..  Site_Admin
    """
    userrole = db.Column(
        db.Enum("annotator", 'experimenter', 'admin',
        name='roleType'),
        server_default="annotator",
        nullable=False
    )

    """ Flag indicating whether the user has turned on the
    looping of clips. It applies for both audio / video.
    """
    looping = db.Column(
        db.Boolean(name='looping'),
        nullable=False,
        server_default='1',
    )

    # """List of the user's roles."""
    # roles = db.relationship('Role', secondary=userrole,
    # backref=db.backref('users', lazy='dynamic'))

    @classmethod
    def get_by_username(cls, username):
        """Get profile by username.
        .. note:: The username is not case sensitive.
        """
        return cls.query.filter(
            User.username == username
        ).one()

    @classmethod
    def get_by_userid(cls, user_id):
        """Get profile by user identifier.
        :param user_id: The :class:`models.User.id` ID.
        :returns: A :class:`models.User` instance
            or ``None``.
        """
        return cls.query.filter_by(id=user_id).one_or_none()

    def __str__(self):
        """Representation."""
        return 'User <id={0.id}, email={0.email}>'.format(self)

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
