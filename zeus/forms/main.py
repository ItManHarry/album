from flask_wtf import FlaskForm
from wtforms import TextAreaField,SubmitField
from wtforms.validators import DataRequired, Length
class PhotoForm(FlaskForm):
    description = TextAreaField('描述', validators=[DataRequired('请输入描述!!!'), Length(10, 255, '长度介于10~255之间!!!')])
    submit = SubmitField('保存')
class PhotoCommentForm(FlaskForm):
    content = TextAreaField('评论', validators=[DataRequired('请输入评论!!!'), Length(10, 255, '长度介于10~255之间!!!')])
    submit = SubmitField('发表')