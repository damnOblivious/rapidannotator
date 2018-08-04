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
        'User.id')),
    db.Column('Experiment_id', db.Integer, db.ForeignKey(
        'Experiment.id'))
)

''' TODO? no need to specify datatype in ForeignKeys '''

"""User data model."""
class User(UserMixin, db.Model):

    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    """Lower-case username to assert uniqueness."""
    username = db.Column(db.String(255), nullable=False, unique=True)

    """Full name of person."""
    fullname = db.Column(db.String(255), nullable=False, server_default='')

    """User email."""
    email = db.Column(db.String(120), nullable=False, unique=True)

    """User password."""
    password = db.Column(db.String(300))

    """ There are 3 levels of user hierarchy,
     User can be any one / more of
    ..  Annotator,
    ..  Experimenter,
    ..  Site_Admin
    ..  by default everyone will be annotator
    """
    experimenter = db.Column(
        db.Boolean(name='experimenter'),
        nullable=False,
        server_default='1',
    )

    admin = db.Column(
        db.Boolean(name='admin'),
        nullable=False,
        server_default='1',
    )

    """ Flag indicating whether the user has turned on the
    looping of clips. It applies for both audio / video.
    """
    looping = db.Column(
        db.Boolean(name='looping'),
        nullable=False,
        server_default='1',
    )

    def is_experimenter(self):
        return self.experimenter

    def is_admin(self):
        return self.admin

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

    """ One to Many relation
    ..  For User:
    ..  list of the AnnotationInfo associated with this user.
    """
    annotationInfo = db.relationship("AnnotationInfo", cascade='all, delete-orphan',
                passive_deletes=True
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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    '''the experiment with which user is associated.'''
    experiment_id = db.Column(Integer, db.ForeignKey(
        'Experiment.id', ondelete='CASCADE'))

    '''the user associated with this experiment.'''
    user_id = db.Column(Integer, db.ForeignKey(
    'User.id', ondelete='CASCADE'))

    start = db.Column(db.Integer, nullable=False, server_default="0")
    end = db.Column(db.Integer, nullable=False, server_default="-1")
    current = db.Column(db.Integer, nullable=False, server_default="0")

    """ many to one relation
    ..  from an AnnotatorAssociation instance
    ..  to an Experiment instance
    """
    experiment = db.relationship('Experiment', uselist=False,
                lazy=True, backref=db.backref(
                    'annotators', cascade='all, delete-orphan',
                    passive_deletes=True, lazy=True)
    )

class Experiment(db.Model):
    """Experiment data model."""

    __tablename__ = "Experiment"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

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

    """ Experiments can have files uploaded via one of the 2 types
    ..  manual : Manually,
    ..  viaSpreadsheet,
    """
    uploadType = db.Column(
        db.Enum('manual', 'viaSpreadsheet',
        name='uploadType'),
        nullable=False,
        server_default='manual',
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
                    cascade='all, delete-orphan', passive_deletes=True)

    """ One to Many relation
    ..  For all types of Experiments:
    ..  list of the annoatation levels that are associated with
    ..  that experiment.
    """
    annotation_levels = db.relationship("AnnotationLevel",
                            cascade='all, delete-orphan', passive_deletes=True
    )

    # """ One to Many relation
    # ..  For Text Experiments:
    # ..  the text content for each file.
    # """
    # text_files = db.relationship("TextFile", lazy='dynamic',
    #         cascade='all, delete-orphan', passive_deletes=True
    # )

    """ One to Many relation
    ..  For Images / Audio / Video Experiments:
    ..  the link / url / path to the actual content of each file.
    """
    files = db.relationship("File", lazy='dynamic',
            cascade='all, delete-orphan', passive_deletes=True
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

"""
    Annotation Level to store a level of annoatation.
    ..  For Example: `Gender` is an annotation level,
    ..  that stores gender of a person.
    ..  It will have labels like : Male, Female and so on.
"""
class AnnotationLevel(db.Model):
    __tablename__ = 'AnnotationLevel'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    '''the experiment with which the this Annotation Level is associated.'''
    experiment_id = db.Column(Integer, db.ForeignKey(
        'Experiment.id', ondelete='CASCADE')
    )

    ''' name
    ..  name of the annotation level like Gender or Age.
    ..  it can be of maximum length 32 characters
    '''
    name = db.Column(db.String(32), nullable=False, server_default='')

    ''' description
    ..  a small description of the annotation.
    ..  via this Experiment Owner can explain that what an annotator
    ..  is expected to look for while annotating this annotation level.
    ..  size is limited to 640 characters
    '''
    description = db.Column(db.String(640), nullable=False, server_default='')

    ''' level_number
    ..  decides the order in which an annotator is asked
    ..  to annotate a particular data item.
    '''
    level_number = db.Column(db.Integer, nullable=False)

    """ One to Many relation
    ..  For AnnotationLevel:
    ..  list of the labels associated with this annotation level.
    """
    labels = db.relationship("Label", cascade='all, delete-orphan',
                passive_deletes=True
    )

    """ One to Many relation
    ..  For AnnotationLevel:
    ..  list of the AnnotationInfo associated with this annotation level.
    """
    annotationInfo = db.relationship("AnnotationInfo", cascade='all, delete-orphan',
                passive_deletes=True
    )

    def __str__(self):
        """Representation."""
        return 'AnnotationLevel <id={0.id}, \
                Experiment={0.experiment_id}, \
                name={0.name}, \
                description={0.description}, \
                level_number={0.level_number}>'.format(self)

    def __repr__(self):
        return 'AnnotationLevel <id={0.id}, \
                Experiment={0.experiment_id}, \
                name={0.name}, \
                description={0.description}, \
                level_number={0.level_number}>'.format(self)

"""
    Label of an annoatation level.
    ..  For Example: If AnnotationLevel is `Gender`,
    ..  that stores gender of a person.
    ..  It will have Lable(s) like : `Male`, `Female` and so on.
"""
class Label(db.Model):
    __tablename__ = 'Label'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    '''the annotation with which the this Label is associated.'''
    annotation_id = db.Column(Integer, db.ForeignKey(
        'AnnotationLevel.id', ondelete='CASCADE')
    )

    ''' name
    ..  name of the label like `Male` or `Female`.
    ..  it can be of maximum length 32 characters
    '''
    name = db.Column(db.String(32), nullable=False, server_default='')

    ''' key_binding
    ..  the key bound to a label : For Example: 'a' is associated with Male
    ..  when User will press that key :
    '''
    key_binding = db.Column(db.String(1), nullable=False, server_default='')

    """ One to Many relation
    ..  For Label:
    ..  list of the AnnotationInfo associated with this label.
    """
    annotationInfo = db.relationship("AnnotationInfo", cascade='all, delete-orphan',
                passive_deletes=True
    )

    def __str__(self):
        """Representation."""
        return 'Label <id={0.id}, \
                Annotation={0.annotation_id}, \
                name={0.name}, \
                key_binding={0.key_binding}>'.format(self)

    def __repr__(self):
        return 'Label <id={0.id}, \
                Annotation={0.annotation_id}, \
                name={0.name}, \
                key_binding={0.key_binding}>'.format(self)

# """
#     TextFile model to store the text contents of the Text Experiments
# """
# class TextFile(db.Model):
#     __tablename__ = 'TextFile'
#
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#
#     '''the experiment with which the this text file is associated.'''
#     experiment_id = db.Column(Integer, db.ForeignKey(
#         'Experiment.id', ondelete='CASCADE')
#     )
#
#     ''' caption
#     ..  a small description of the text.
#     ..  size is limited to 320 characters
#     '''
#     caption = db.Column(db.String(320), nullable=False, server_default='')
#
#     ''' content
#     ..  the actual text to be annotated.
#     ..  size is limited to 65000 characters.
#     ..  size limit of TEXT field of MySQL is 65535
#     ..  the maximum table row size allowed is 65535 including storing overheads.
#     '''
#     content = db.Column(db.String(65000), nullable=False, server_default='')
#
#     def __str__(self):
#         """Representation."""
#         return 'TextFile <id={0.id}, \
#                 Experiment={0.experiment_id}, \
#                 caption={0.caption}, \
#                 content={0.content}>'.format(self)
#
#     def __repr__(self):
#         return 'TextFile <id={0.id}, \
#                 Experiment={0.experiment_id}, \
#                 caption={0.caption}, \
#                 content={0.content}>'.format(self)

"""
    File model to store the caption and
    path to the contents in case of Audio / Video / Image experiments and
    actual contents in case of Text experiments.
"""
class File(db.Model):
    __tablename__ = 'File'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    '''the experiment with which the this text file is associated.'''
    experiment_id = db.Column(Integer, db.ForeignKey(
        'Experiment.id', ondelete='CASCADE')
    )

    ''' name
    ..  name(editatble) of the uploaded file.
    ..  size is limited to 1024 characters
    '''
    name = db.Column(db.String(1024), nullable=False, server_default='')

    ''' caption
    ..  a small description of the text.
    ..  size is limited to 320 characters
    '''
    caption = db.Column(db.String(320), nullable=False, server_default='')

    ''' content
    ..  actual text to be annotated for Text experiments.
    ..  url / path of the content / file to be displayed
    ..  for Audio / Video / Image experiments
    ..  size is limited to 2^15 characters.
    ..  size limit of TEXT field of MySQL is 65535
    ..  the maximum table row size allowed is 65535 including storing overheads.
    '''
    content = db.Column(db.String(32768), nullable=False, server_default='')

    """ One to Many relation
    ..  For File:
    ..  list of the AnnotationInfo associated with this file.
    """
    annotationInfo = db.relationship("AnnotationInfo", cascade='all, delete-orphan',
                passive_deletes=True
    )

    def __str__(self):
        """Representation."""
        return 'File <id={0.id}, \
                Experiment={0.experiment_id}, \
                caption={0.caption}, \
                name={0.name}, \
                content={0.content}>'.format(self)

    def __repr__(self):
        return 'File <id={0.id}, \
                Experiment={0.experiment_id}, \
                caption={0.caption}, \
                name={0.name}, \
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
        'Experiment.id', ondelete='CASCADE')
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

"""
    AnnotationInfo of an annoatation level, user, file.
"""
class AnnotationInfo(db.Model):
    __tablename__ = 'AnnotationInfo'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    '''the annotation with which the this AnnotationInfo is associated.'''
    annotationLevel_id = db.Column(Integer, db.ForeignKey(
        'AnnotationLevel.id', ondelete='CASCADE')
    )

    '''the annotator with which the this AnnotationInfo is associated.'''
    user_id = db.Column(Integer, db.ForeignKey(
        'User.id', ondelete='CASCADE')
    )

    '''the file with which the this AnnotationInfo is associated.'''
    file_id = db.Column(Integer, db.ForeignKey(
        'File.id', ondelete='CASCADE')
    )

    '''the label set by the annotator.'''
    label_id = db.Column(Integer, db.ForeignKey(
        'Label.id', ondelete='CASCADE')
    )

    def __str__(self):
        """Representation."""
        return 'AnnotationInfo <id={0.id}, \
                annotationLevel_id={0.annotationLevel_id}, \
                user_id={0.user_id}, \
                label_id={0.label_id}, \
                file_id={0.file_id}>'.format(self)

    def __repr__(self):
        return 'AnnotationInfo <id={0.id}, \
                annotationLevel_id={0.annotationLevel_id}, \
                user_id={0.user_id}, \
                label_id={0.label_id}, \
                file_id={0.file_id}>'.format(self)


"""
    RightsRequest of users.
"""
class RightsRequest(db.Model):
    __tablename__ = 'RightsRequest'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    ''' id of the user who made this request.'''
    user_id = db.Column(Integer, db.ForeignKey(
        'User.id', ondelete='CASCADE')
    )

    ''' username of the user who made this request.'''
    username = db.Column(db.String(255), db.ForeignKey(
        'User.username', ondelete='CASCADE')
    )

    """
    ..  Each user has Annotator Rights in the beginning,
        User can request to become any one of
    ..  Experimenter,
    ..  Site_Admin
    """
    role = db.Column(
        db.Enum('experimenter', 'admin',
        name='roleType'),
        nullable=False
    )

    """ User's message for the site_admin. """
    message = db.Column(db.String(640))


    """The date and time when the request was made."""
    requested_at = db.Column(db.DateTime, server_default=func.now())

    """
        Flag indicating whether the request has been approved or not.
    """
    approved = db.Column(
        db.Boolean(name='approved'),
        nullable=False,
        server_default='0',
    )

    def __str__(self):
        """Representation."""
        return 'RightsRequest <id={0.id}, \
                id={0.id}, \
                user_id={0.user_id}, \
                role={0.role}, \
                requested_at={0.requested_at}, \
                approved={0.approved}, \
                message={0.message}>'.format(self)

    def __repr__(self):
        return 'RightsRequest <id={0.id}, \
                id={0.id}, \
                user_id={0.user_id}, \
                role={0.role}, \
                requested_at={0.requested_at}, \
                approved={0.approved}, \
                message={0.message}>'.format(self)
