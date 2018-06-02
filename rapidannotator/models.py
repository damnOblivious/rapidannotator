from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import Enum, String, Integer, Boolean, DateTime
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.sql import func

from flask_login import UserMixin
from flask_security import RoleMixin

from rapidannotator.validators import validate_username
from rapidannotator import login

db = SQLAlchemy()

"""Experiments that a User owns."""
ExperimentOwner = db.Table(
    'ExperimentOwner',
    db.Column('User_id', db.Integer, db.ForeignKey(
        'User.id'), primary_key=True),
    db.Column('Experiment_id', db.Integer, db.ForeignKey(
        'Experiment.id'), primary_key=True)
)

"""User data model."""
class User(UserMixin, db.Model):

    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key=True)

    """Lower-case username to assert uniqueness."""
    username = db.Column(db.String(255), nullable=False, unique=True)

    """Full name of person."""
    fullname = db.Column(db.String(255), nullable=False, server_default='')

    """User email."""
    email = db.Column(db.String(120), nullable=False, unique=True)

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

    '''List of the experiments owns.'''
    my_experiments = db.relationship("Experiment", secondary=ExperimentOwner,
                lazy='dynamic', backref=db.backref('owners',
                lazy='dynamic')
    )

    """ List of experiments user has to annotate
        one to many relation
    ..  from User
    ..  to an AnnotatorAssociation instance
    """
    experiments_to_annotate = db.relationship("AnnotatorAssociation",
                lazy=True, backref=db.backref('annotator',
                lazy=True)
    )

    def __str__(self):
        """Representation."""
        return 'User <id={0.id}, \
                username={0.username}, \
                fullname={0.fullname}, \
                email={0.email}>'.format(self)

    def __repr__(self):
        return 'User <id={0.id}, \
                username={0.username}, \
                fullname={0.fullname}, \
                email={0.email}>'.format(self)

"""Association table for the experiments annotators.(annotator association table)"""
class AnnotatorAssociation(db.Model):

    __tablename__ = 'AnnotatorAssociation'

    '''the experiment with which user is associated.'''
    experiment_id = db.Column(Integer, db.ForeignKey(
        'Experiment.id'), primary_key=True
    )

    '''the user associated with this experiment.'''
    user_id = db.Column(Integer, db.ForeignKey(
    'User.id'), primary_key=True
    )

    start = db.Column(db.Integer, nullable=False, server_default="0")
    end = db.Column(db.Integer, nullable=False, server_default="-1")
    current = db.Column(db.Integer, nullable=False, server_default="0")

    """ many to one relation
    ..  from an AnnotatorAssociation instance
    ..  to an Experiment instance
    """
    experiment = db.relationship('Experiment',
                lazy=True, backref=db.backref('annotators',
                lazy=True)
    )

class Experiment(db.Model):
    """Experiment data model."""

    __tablename__ = "Experiment"

    id = db.Column(db.Integer, primary_key=True)

    """Name of the Experiment"""
    name = db.Column(db.String(255), nullable=False, unique=True)

    """A short description about the experiment."""
    description = db.Column(db.String(320), nullable=False, server_default='')

    """The date and time when the experiment was created."""
    created_at = db.Column(db.DateTime, server_default=func.now())

    """ Experiments can have one of the 4 types of files
    ..  Audios,
    ..  Videos,
    ..  Images,
    ..  texts
    """
    category = db.Column(
        db.Enum('audio', 'video', 'image', 'text',
        name='category'),
        nullable=False
    )

    """ Experiments can have one of the 2 types of status
    ..  Completed,
    ..  In Progress,
    """
    status = db.Column(
        db.Enum('Completed', 'In Progress',
        name='status'),
        server_default="In Progress",
        nullable=False,
    )

    def __str__(self):
        """Representation."""
        return 'Experiment <id={0.id}, \
                name={0.name}, \
                description={0.description}, \
                category={0.category}>'.format(self)

    def __repr__(self):
        return 'Experiment <id={0.id}, \
                name={0.name}, \
                description={0.description}, \
                category={0.category}>'.format(self)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
