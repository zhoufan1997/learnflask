import os

baseidr = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY =os.environ.get('SECRET_KEY')or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'zf11911@163.com'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = "zf11911@163.com"
    MAIL_PASSWORD = "zf3662188"


    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql://zhoufan:123456@localhost:3306/test?charset=gb2312'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://zhoufan:123456@localhost:3306/test?charset=gb2312'





config = {
    'development': DevelopmentConfig,
    'testing':TestingConfig,
    'default': DevelopmentConfig
}


