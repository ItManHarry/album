from datetime import datetime
from flask_login import UserMixin
from zeus.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
'''
    系统角色权限关联表(多对多)
'''
roles_permissions = db.Table('roles_permissions',
    db.Column('role_id', db.String(32), db.ForeignKey('role.id')),
    db.Column('permission_id', db.String(32), db.ForeignKey('permission.id'))
)
'''
    系统角色
    - 访客(Guest) : 仅可访问页面
    - 被禁用户(Forbidden) : 仅可访问页面
    - 被锁定用户(Locked) : FOLLOW, COLLECT
    - 普通用户(User) : FOLLOW, COLLECT, COMMENT, UPLOAD
    - 协管员(Moderator) : 普通用户权限+MODERATE
    - 管理员(Administrator) : 具有系统所有权限
'''
class Role(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(30), unique=True)        #角色名称(唯一)
    permissions = db.relationship('Permission', secondary='roles_permissions', back_populates='roles')
    users = db.relationship('User', back_populates='role')
    #初始化角色权限
    @staticmethod
    def init_role():
        roles_permissions_map = {
            'Locked': ['FOLLOW','COLLECT'],
            'User': ['FOLLOW','COLLECT','COMMENT','UPLOAD'],
            'Moderator': ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD','MODERATE'],
            'Administrator': ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD','MODERATE','ADMINISTRATOR']
        }
        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(id=uuid.uuid4().hex,name=role_name)
                db.session.add(role)
            role.permissions = []
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(name=permission_name).first()
                if permission is None:
                    permission = Permission(id=uuid.uuid4().hex,name=permission_name)
                    db.session.add(permission)
                role.permissions.append(permission)
        db.session.commit()
'''
    系统权限
    - 关注用户: FOLLOW
    - 收藏图片：COLLECT
    - 发布评论：COMMENT
    - 上传图片：UPLOAD
    - 协管员：  MODERATE
    - 管理员：  ADMINISTRATOR
'''
class Permission(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(30), unique=True)        #权限名称(唯一)
    roles = db.relationship('Role', secondary='roles_permissions',back_populates='permissions')
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
    active = db.Column(db.Boolean, default=False)                   #已激活
    logins = db.relationship('Login', back_populates='user')        # 登录履历-反向关联
    role_id = db.Column(db.String(32), db.ForeignKey('role.id'))    #所属角色
    role = db.relationship('Role', back_populates='users')
    # 设置密码-使用werkzeug.security提供的加密方式
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    # 校验密码
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)
'''
    登录履历
'''
class Login(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)     #登录时间
    user_id = db.Column(db.String(32), db.ForeignKey('user.id'))                #登录账号
    user = db.relationship('User', back_populates='logins')                     #登录人员-反向关联