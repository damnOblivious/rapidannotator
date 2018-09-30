# All variables should be uppercase

class BaseConfig(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'mysql://[username]:[password]@localhost/[database_name]'
    SECRET_KEY = "sldjfhals13 2hhdwflkjdhfa"
    UPLOAD_FOLDER = '[Path_to_storage_directory]'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_ECHO = True
    LOGIN_DISABLED = False
