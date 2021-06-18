from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, DateField, HiddenField, PasswordField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError, validators
from flask_login import current_user
from zeus.models import User
'''
    修改个人信息
'''
class ProfileForm(FlaskForm):
    code = StringField('账号', validators=[DataRequired('请输入账号!!!'), Length(1, 20, '长度要介于1~20!!!'),
                                         Regexp('^[a-zA-Z0-9]*$', message='账号只能包含[a-z,A-Z,0-9]!!!')])
    name = StringField('昵称', validators=[DataRequired('请输入用户名!!!'), Length(1, 30, '长度要介于1~30!!!')])
    email = StringField('邮箱', validators=[DataRequired('请输入邮箱!!!'), Length(1, 64, '长度要介于1~64!!!'), Email('邮箱格式不正确!!!')])
    website = StringField('个人网址')
    location = StringField('地址')
    birthday = DateField('生日', [validators.optional()])  # 非必填
    submit = SubmitField('保存')

    def validate_email(self, field):
        if field.data.lower() != current_user.email and User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('邮箱已注册!!!')

    def validate_code(self, field):
        if field.data.lower() != current_user.code and User.query.filter_by(code=field.data.lower()).first():
            raise ValidationError('账号已注册!!!')
class AvatarForm(FlaskForm):
    image = FileField('上传(<=3M)', validators=[FileRequired(), FileAllowed(['jpg', 'png'], '只允许上传.jpg和.png格式图片!!!')])
    submit = SubmitField('上传')
class CropAvatarForm(FlaskForm):
    x = HiddenField()
    y = HiddenField()
    w = HiddenField()
    h = HiddenField()
    submit = SubmitField('保存')
'''
    密码重置表单
'''
class ResetPasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired('请输入旧密码!!!'), Length(8, 128, '长度要介于8~128!!!')])
    new_password = PasswordField('新密码', validators=[DataRequired('请输入新密码!!!'), Length(8, 128, '长度要介于8~128!!!'), EqualTo('new_password_confirm', message='新密码不一致!!!')])
    new_password_confirm = PasswordField('确认新密码', validators=[DataRequired('请确认新密码!!!')])
    submit = SubmitField('保存')
'''
    注销用户表单
'''
class DestroyUserForm(FlaskForm):
    code = StringField('账号', validators=[DataRequired('请输入账号!!!'), Length(1, 20, '长度要介于1~20!!!')])
    def validate_code(self, field):
        if field.data == 'admin':
            raise ValidationError('管理员不能注销!!!')
        if field.data != current_user.code:
            raise ValidationError('账号错误!!!')
