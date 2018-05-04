import os

baseidr = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY =os.environ.get('SECRET_KEY')or 'hard to guess string'   #密钥
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True                             #每次请求结束都会自动提交数据库中的变动
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'                          #邮箱主题前缀
    FLASKY_MAIL_SENDER = 'zf11911@163.com'                      #发件人默认地址
    SQLALCHEMY_TRACK_MODIFICATIONS = False                        #如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。这需要额外的内存， 如果不必要的可以禁用它
    FLASKY_ADMIN = "zf11911@163.com"                          #电子邮件收件人
    MAIL_SERVER = 'smtp.163.com'                            #email server
    MAIL_PORT = 465                                          #电子邮件端口号
    MAIL_USE_SSL = True                                     #ssl安全套接层
    MAIL_USERNAME = "zf11911@163.com"                      #电子邮箱用户名
    MAIL_PASSWORD = "zf3662188"                            #电子邮箱密码
    FLASKY_POSTS_PER_PAGE = 10                                #配置每页博客的显示数量


    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql://zhoufan:123456@localhost:3306/test?charset=gb2312' #数据库默认地址

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://zhoufan:123456@localhost:3306/test?charset=gb2312'





config = {
    'development': DevelopmentConfig,
    'testing':TestingConfig,
    'default': DevelopmentConfig           #默认配置
}


