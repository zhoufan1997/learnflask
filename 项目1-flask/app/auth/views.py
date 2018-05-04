from flask_login import login_user
from . import auth
from flask import render_template,flash,request,url_for,redirect
from ..models import User
from .froms import LoginForm,RegistarationForm
from .. import  db
from ..email import send_email
from flask_login import current_user,login_required,logout_user


@auth.before_app_request
def before_request():
    if current_user.is_authenticated :
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/login',methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next')or url_for('main.index'))
        flash('无效的用户名或密码')
    return render_template('auth/login.html',form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已注销')
    return redirect(url_for('main.index'))

@auth.route('/register',methods = ['GET','POST'])
def register():       #注册新用户的表单路由
    form = RegistarationForm()
    if form.validate_on_submit():
        user = User( email=form.email.data, username=form.username.data,password = form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email,'Confirm you account','auth/email/confirm',user=user,token=token)
        flash('确认电子邮件已通过电子邮件发送给您')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('你已经确认你的账户。谢谢!')
    else:
        flash('确认链接无效或已过期')
    return redirect(url_for('main.index'))




@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
         return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Accout', 'auth/email/comfirm', user=current_user, token=token)
    flash('新的确认电子邮件已通过电子邮件发送给您.')
    return redirect(url_for('main.index'))

