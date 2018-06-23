# All variables should be uppercase

class BaseConfig(object):
    DEBUG = False
    TESTING = False

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://tissues:12345@localhost/testing'
    SQLALCHEMY_ECHO = True
    SECRET_KEY = "sldjfhals13 2hhdwflkjdhfa"
    UPLOAD_FOLDER = '/home/tissues/interests/lal/rapidannotator/uploads'
