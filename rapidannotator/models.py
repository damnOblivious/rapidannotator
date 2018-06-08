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

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

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

    """ One to One relation
    ..  For Audio / Video Experiments:
    ..  details of duration of the display time of the audio / video.
    """
    display_time = db.relationship("DisplayTime", uselist=False,
                            cascade='all, delete-orphan')

    """ One to Many relation
    ..  For Text Experiments:
    ..  the text content for each file.
    """
    text_file = db.relationship("TextFile", cascade='all, delete-orphan')

    """ One to Many relation
    ..  For Images / Audio / Video Experiments:
    ..  the link / url / path to the actual content of each file.
    """
    file = db.relationship("File", cascade='all, delete-orphan')

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

"""
    TextFile model to store the text contents of the Text Experiments
"""
class TextFile(db.Model):
    __tablename__ = 'TextFile'

    id = db.Column(db.Integer, primary_key=True)

    '''the experiment with which the this text file is associated.'''
    experiment_id = db.Column(Integer, db.ForeignKey(
        'Experiment.id'), primary_key=True
    )

    ''' caption
    ..  a small description of the text.
    ..  size is limited to 320 characters
    '''
    caption = db.Column(db.String(320), nullable=False, server_default='')

    ''' content
    ..  the actual text to be annotated.
    ..  size is limited to 65000 characters.
    ..  size limit of TEXT field of MySQL is 65535
    ..  the maximum table row size allowed is 65535 including storing overheads.
    '''
    content = db.Column(db.String(65000), nullable=False, server_default='')

    def __str__(self):
        """Representation."""
        return 'TextFile <id={0.id}, \
                Experiment={0.experiment_id}, \
                caption={0.caption}, \
                content={0.content}>'.format(self)

    def __repr__(self):
        return 'TextFile <id={0.id}, \
                Experiment={0.experiment_id}, \
                caption={0.caption}, \
                content={0.content}>'.format(self)

"""
    File model to store the path to the contents of the Experiments
    of the type Audio / Video / Image.
"""
class File(db.Model):
    __tablename__ = 'File'

    id = db.Column(db.Integer, primary_key=True)

    '''the experiment with which the this text file is associated.'''
    experiment_id = db.Column(Integer, db.ForeignKey(
        'Experiment.id'), primary_key=True
    )

    ''' caption
    ..  a small description of the text.
    ..  size is limited to 320 characters
    '''
    caption = db.Column(db.String(320), nullable=False, server_default='')

    ''' url
    ..  the actual url / path of the content / file to be displayed
    '''
    url = db.Column(db.String(1024), nullable=False, server_default='')

    def __str__(self):
        """Representation."""
        return 'File <id={0.id}, \
                Experiment={0.experiment_id}, \
                caption={0.caption}, \
                url={0.url}>'.format(self)

    def __repr__(self):
        return 'File <id={0.id}, \
                Experiment={0.experiment_id}, \
                caption={0.caption}, \
                url={0.url}>'.format(self)

"""
    DisplayTime model to store duration for which the
    video / audio will be played:
"""
class DisplayTime(db.Model):
    __tablename__ = 'DisplayTime'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    '''the experiment with which the duration is associated.'''
    experiment_id = db.Column(Integer, db.ForeignKey(
        'Experiment.id'), primary_key=True
    )

    ''' before_time
    ..  the time relative to the time given in the link
    ..  to display the video / audio.
    ..  For example if the time(in seconds) in the link is 1540
    ..  and before time is 13 then the actual time when the video
    ..  will start will be 1553 (1540 + 13)
    '''
    before_time = db.Column(db.Integer, nullable=False, server_default="0")

    ''' after_time
    ..  the time relative to the time given in the link
    ..  to display the video / audio.
    ..  For example if the time(in seconds) in the link is 1540
    ..  and after time is 27 then the actual time when the video
    ..  will end will be 1567 (1540 + 27).
    ..  Default value(-1) implies the video will be played till the end.
    '''
    after_time = db.Column(db.Integer, nullable=False, server_default="-1")

    def __str__(self):
        """Representation."""
        return 'DisplayTime <id={0.id}, \
                Experiment={0.experiment_id}, \
                before_time={0.before_time}, \
                after_time={0.after_time}>'.format(self)

    def __repr__(self):
        return 'DisplayTime <id={0.id}, \
                Experiment={0.experiment_id}, \
                before_time={0.before_time}, \
                after_time={0.after_time}>'.format(self)
