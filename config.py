# Authors: Zainab Batool & Tessa Pham

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ELASTICSEARCH_URL='http://localhost:9200'
    LANGUAGES = ['en']
    POSTS_PER_PAGE = 25
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['tessagrethen@gmail.com', 'batool.zainab98@gmail.com']
    WTF_CSRF_ENABLED = False

    
class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

class FunctionalTestingConfig(TestingConfig):
    WTF_CSRF_ENABLED = False