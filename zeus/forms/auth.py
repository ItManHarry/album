from flask_wtf import  FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from zeus.models import User
#用户注册Form
class RegisterForm(FlaskForm):
    code = StringField('账号', validators=[DataRequired('请输入账号!!!'), Length(1,20,'长度要介于1~20!!!'), Regexp('^[a-zA-Z0-9]*$', message='账号只能包含[a-z,A-Z,0-9]!!!')])
    name = StringField('昵称', validators=[DataRequired('请输入用户名!!!'), Length(1,30,'长度要介于1~30!!!')])
    password = PasswordField('密码', validators=[DataRequired('请输入密码!!!'), Length(8,128,'长度要介于8~128!!!'),EqualTo('password_confirm',message='密码不一致!!!')])
    password_confirm = PasswordField('确认密码', validators=[DataRequired('请确认密码!!!')])
    email = StringField('邮箱', validators=[DataRequired('请输入邮箱!!!'), Length(1,64,'长度要介于1~64!!!'), Email('邮箱格式不正确!!!')])
    website = StringField('个人网址')
    location = StringField('地址')
    submit = SubmitField('注册')
    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('邮箱已注册!!!')
    def validate_code(self, field):
        if User.query.filter_by(code=field.data.lower()).first():
            raise ValidationError('账号已注册!!!')