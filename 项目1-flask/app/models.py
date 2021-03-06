from  app import  db
from werkzeug.security import generate_password_hash,check_password_hash
from . import login_manager
from flask_login import UserMixin,AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import  current_app,request
from datetime import datetime
from config import config
import  hashlib
from markdown import markdown
import bleach


class Permission:
    FOLLOW = 0x01             # 关注用户
    COMMENT = 0x02            # 在他人的文章中发表评论
    WRITE_ARTICLES = 0x04     # 写文章
    MODERATE_COMMENTS = 0x08  # 管理他人发表的评论
    ADMINISTRATOR = 0xff      # 管理者权限



class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean,default=False,index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User',backref = 'role',lazy = 'dynamic')

    
    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),  # 只有普通用户的default为True
            'Moderare': (Permission.FOLLOW | Permission.COMMENT |
                         Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by( name=r ).first()
            if role is None:
                role = Role( name=r )
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add( role )
        db.session.commit()


    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm



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
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(),default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow)
    avatar_hash = db.Column( db.String( 32 ) )
    posts = db.relationship('Post',backref='author',lazy='dynamic')

    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions = 0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default = True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()


    @property
    def password(self):
        raise AttributeError('密码不是可读属性')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash( self.password_hash, password )


    def gravatar_hash(self):               #头像
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):    #头像
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def ping(self):          #刷新用户的最后访问时间
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def generate_confirmation_token(self,expiration=3600):      #生成一个令牌 ，默认时间是3600
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id}).decode('utf-8')


    def confirm(self,token):          #检验令牌
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



    def __repr__(self):
        return '<User %r>' % self.username

    def can(self, perm):
        return self.role is not None and self.role.has_permission( perm )

    def is_administrator(self):  #检查管理员权限
        return self.can(Permission.ADMINISTRATOR)
    @staticmethod
    def generate_fake(count=100):                  #虚拟数据测试
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email = forgery_py.internet.email_address(),
                     username = forgery_py.internet.user_name(True),
                     password = forgery_py.lorem_ipsum.word(),
                     confirmed = True,
                     name = forgery_py.name.full_name(),
                     location = forgery_py.address.city(),
                     about_me = forgery_py.lorem_ipsum.sentence(),
                     member_since = forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False
    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader     #加载用户的回调函数
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    _tablename_ = 'posts'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)

    @staticmethod
    def generate_fake(count=100):          #虚拟博客文章数据，使用forgery_py
        from random import seed,randint
        import forgery_py
        seed()
        user_count=User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0,user_count-1)).first()
            p = Post(body = forgery_py.lorem_ipsum.sentences(randint(1,3)),
                     timestamp = forgery_py.date.date(True),
                     author = u
                     )
            db.session.add(p)
            db.session.commit()
    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowde_tags= ['a','abbr','acronym','b','blockquote','code','em','i',
                       'li','pre','ol','strong','ul','h1','h2','h3','p']
        target.body_html = bleach.linkify(bleach.clean(markdown(value,output_format='html'),tags=allowde_tags,strip=True))

db.event.listen(Post.body,'set',Post.on_changed_body)