from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Email, Regexp
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