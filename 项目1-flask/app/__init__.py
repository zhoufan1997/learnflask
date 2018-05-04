from flask import Flask
from flask import flash,session,redirect,url_for,render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from flask_script import Shell,Manager
from flask_migrate import Migrate,MigrateCommand
from flask_mail import Mail
from config import config
from flask_login import  LoginManager
from flask_pagedown import  PageDown

bootstatp =Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
pagedown = PageDown()             #初始化Flask-PageDown
login_manager.session_protection = 'srtong'     #提供不同的安全等级防止用户会话被篡改，可选参数有none|basic|srtong
login_manager.login_view = 'auto.login'       #设置登录页面的端点

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstatp.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix = '/auth')


    return app

