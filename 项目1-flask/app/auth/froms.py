from  flask_wtf import FlaskForm
from wtforms import  SubmitField,StringField,PasswordField,BooleanField
from wtforms.validators import DataRequired,Length,Email,Regexp,EqualTo,Required
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('电子邮箱',validators=[DataRequired(),Length(1,64),Email()])
    password = PasswordField('密码',validators=[DataRequired()])
    remember_me = BooleanField('记住我的密码')
    submit = SubmitField('登录')

class RegistarationForm(FlaskForm):
    email = StringField('电子邮件',validators=[DataRequired(),Length(1,64),Email()])
    username = StringField('姓名',validators=[DataRequired(),Length(1,64),
                                                  Regexp('[A-Za-z][A-Za-z0-9_.]*$',0,
                                                         'Usernames must hava only letters,'
                                                         'numbers,dapts pr imderscpres')])
    password = PasswordField('密码',validators=[DataRequired(),EqualTo('password2',message='Password must match')])
    password2 = PasswordField('确认密码',validators=[DataRequired()])
    submit = SubmitField('注册')

    def validtae_email(self, field):
        if User.query.filter_by(email = field.data).first():
            raise ValidationError('电子邮箱已经注册')

    def validate_username(self,field):
        if User.query.filter_by(username = field.data).first():
            raise ValidationError('用户名已经使用')