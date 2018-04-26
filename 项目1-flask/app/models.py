from  app import  db
from werkzeug.security import generate_password_hash,check_password_hash
from . import login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import  current_app


class Permission:
    FOLLOW = 0*1
    COMMENT = 0*2
    WRITE = 0*4
    MODERATE = 0*8
    ADMIN = 0*80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean,default=False,index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User',backref = 'role',lazy = 'dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),unique=True,index=True)
    username = db.Column( db.String( 64 ), unique=True, index=True )
    password_hash = db.Column(db.String(128))
    role_id = db.Column( db.Integer, db.ForeignKey( 'roles.id' ) )
    confirmed = db.Column(db.Boolean,default=False)

    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id}).decode('utf-8')


    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    @property
    def password(self):
        raise AttributeError('密码不是可读属性e')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



