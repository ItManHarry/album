from datetime import datetime
from flask_login import UserMixin
from zeus.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
'''
    系统用户
'''
class User(db.Model, UserMixin):
    id = db.Column(db.String(32), primary_key=True)
    code = db.Column(db.String(20), unique=True, index=True)        #账号
    name = db.Column(db.String(30))                                 #昵称
    password_hash = db.Column(db.String(128))                       #密码
    email = db.Column(db.String(254), unique=True, index=True)      #邮箱
    website = db.Column(db.String(255))                             #个人主页
    bio = db.Column(db.String(120))                                 #？？？
    location = db.Column(db.String(50))                             #地址
    member_since = db.Column(db.DateTime, default=datetime.utcnow)  #注册时间
    # 设置密码-使用werkzeug.security提供的加密方式
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    # 校验密码
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)