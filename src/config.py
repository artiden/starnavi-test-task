import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "jdspIofAQRuiehr734hinfvc76672"
    NUMBER_OF_USERS = 10
    MAX_POST_PER_USER = 10
    MAX_LIKES_PER_USER = 10