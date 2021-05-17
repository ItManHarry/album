from flask import Blueprint, render_template, url_for, redirect, request,flash
from flask_login import login_required, current_user,login_user,logout_user
from zeus.forms.auth import RegisterForm, LoginForm,ResetPasswordForm,ChangePasswordForm
from zeus.models import User,Login
from zeus.extensions import db
from zeus.tools import generate_token,validate_token,redirect_back
from zeus.settings import operations
from zeus.emails import active_account_email,reset_password_email
import uuid
bp_auth = Blueprint('auth', __name__)
@bp_auth.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            id=uuid.uuid4().hex,
            code = form.code.data.lower(),
            name = form.name.data,
            email = form.email.data.lower(),
            website = form.website.data.lower(),
            location = form.location.data,
            bio = ''
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        #生成令牌
        token = generate_token(user=user,operation=operations['confirm'])
        #发送账号激活邮件
        active_account_email(user, token)
        flash('注册成功,请在邮箱中点击激活账号,激活后登陆系统!!!')
        return redirect(url_for('.login'))
    return render_template('auth/register.html', form=form)
@bp_auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.active:
        return redirect(url_for('main.index'))
    if validate_token(user=current_user, token=token, operaion=operations['confirm']):
        flash('验证通过,跳转主页......')
        return redirect(url_for('main.index'))
    else:
        flash('验证失败,重新发送验证邮件......')
        return redirect(url_for('.resend_confirm_email'))
@bp_auth.route('/resend_confirm_email')
@login_required
def resend_confirm_email():
    if current_user.active:
        return redirect(url_for('main.index'))
    # 生成令牌
    token = generate_token(user=current_user, operation=operations['confirm'])
    # 发送账号激活邮件
    active_account_email(current_user, token)
    flash('激活邮件已重新发送,请注意查收！！！')
    return redirect(url_for('main.index'))
#密码重置请求页面
@bp_auth.route('/reset_password', methods=['GET','POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = generate_token(user=user, operation=operations['reset_password'])
            print('Reset password token is : ', token)
            reset_password_email(user=user, token=token)
            flash('密码重置邮件已发送,请登录邮箱点击激活新密码!!!')
            return redirect(url_for('.login'))
        flash('邮箱地址错误!!!')
        return redirect(url_for('.reset_password'))
    return render_template('auth/reset_password.html', form=form)
#密码重置执行页面
@bp_auth.route('/change_password/<token>', methods=['GET','POST'])
def change_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            if validate_token(user=user, token=token, operation=operations['reset_password'], new_password=form.password.data):
                flash('密码已重置,请登录!!!')
                return redirect(url_for('.login'))
            else:
                flash('密码重置失败,令牌无效或已过期,请重新申请!!!')
                return redirect(url_for('.reset_password'))
        flash('邮箱地址错误,请重新申请!!!')
        return redirect(url_for('main.index'))
    return render_template('auth/change_password.html', form=form)
#登录
@bp_auth.route('/login', methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        code = form.code.data
        password = form.password.data
        remember = form.remember.data
        user = User.query.filter_by(code=code.lower()).first()
        if user:
            if user.validate_password(password):
                login_user(user, remember)
                #新增登录履历
                login = Login(id=uuid.uuid4().hex,user_id=user.id)
                db.session.add(login)
                db.session.commit()
                return redirect_back()
            else:
                flash('密码错误!!!')
        else:
            flash('账号不存在!!!')
    return render_template('auth/login.html', form=form)
#登出
@bp_auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))