from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from flask_avatars import Identicon
from zeus.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os
'''
    系统角色权限关联表(多对多)
'''
roles_permissions = db.Table('roles_permissions',
    db.Column('role_id', db.String(32), db.ForeignKey('role.id')),
    db.Column('permission_id', db.String(32), db.ForeignKey('permission.id'))
)
'''
    图片标签关联表(多对多)
'''
photos_tags = db.Table('photos_tags',
    db.Column('photo_id', db.String(32), db.ForeignKey('photo.id')),
    db.Column('tag_id', db.String(32), db.ForeignKey('tag.id'))
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
    关注用户(关注者和被关注者多对多映射)
'''
class Follow(db.Model):
    follower_id = db.Column(db.String(32), db.ForeignKey('user.id'), primary_key=True)      #关注者ID
    follower = db.relationship('User', foreign_keys = [follower_id], back_populates='following', lazy='joined')
    followed_id = db.Column(db.String(32), db.ForeignKey('user.id'), primary_key=True)      #被关注者ID
    followed = db.relationship('User', foreign_keys=[followed_id], back_populates='followers', lazy='joined')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)                             #关注时间
'''
    系统用户
'''
class User(db.Model, UserMixin):
    id = db.Column(db.String(32), primary_key=True)
    code = db.Column(db.String(20), unique=True, index=True)        #账号
    name = db.Column(db.String(30))                                 #昵称
    password_hash = db.Column(db.String(128))                       #密码
    email = db.Column(db.String(254), unique=True, index=True)      #邮箱
    birth = db.Column(db.Date)                                      #生日
    website = db.Column(db.String(255))                             #个人主页
    bio = db.Column(db.String(120))                                 #？？？
    location = db.Column(db.String(50))                             #地址
    member_since = db.Column(db.DateTime, default=datetime.utcnow)  #注册时间
    active = db.Column(db.Boolean, default=False)                   #已激活
    role_id = db.Column(db.String(32), db.ForeignKey('role.id'))    #所属角色(角色外键)
    avatar_s = db.Column(db.String(64))                             #小头像
    avatar_m = db.Column(db.String(64))                             #中头像
    avatar_l = db.Column(db.String(64))                             #大头像
    role = db.relationship('Role', back_populates='users')          #对应角色(反向关联)
    photos = db.relationship('Photo', back_populates='author',cascade='all')#上传图片(反向关联)
    logins = db.relationship('Login', back_populates='user', cascade='all') #登录履历(反向关联)
    collections = db.relationship('Collect', back_populates='collector', cascade='all')#收藏图片
    following = db.relationship('Follow', foreign_keys=[Follow.follower_id], back_populates='follower', lazy='dynamic', cascade='all')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], back_populates='followed', lazy='dynamic', cascade='all')
    #设置密码-使用werkzeug.security提供的加密方式
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    #校验密码
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)
    #生成头像
    def generate_avatars(self):
        avatar = Identicon(cols=8,rows=8,bg_color=(0,0,0)) #自定义行列组成点数及图片背景色
        #avatar = Identicon()
        filenames = avatar.generate(text=self.name)
        self.avatar_s = filenames[0]
        self.avatar_m = filenames[1]
        self.avatar_l = filenames[2]
        db.session.commit()
    #是否管理员
    @property
    def is_admin(self):
        return self.role.name == 'Administrator'
    #是否具有对应的权限
    def permitted(self, permission_name):
        permission = Permission.query.filter_by(name=permission_name).first()
        return permission is not None and self.role is not None and permission in self.role.permissions
    #收藏图片
    def collect(self, photo):
        if not self.has_collected(photo) and self != photo.author:
            collect = Collect(collector=self, collected=photo)
            db.session.add(collect)
            db.session.commit()
    #取消收藏
    def uncollect(self, photo):
        collect = Collect.query.filter_by(collector_id=self.id).filter_by(collected_id=photo.id).first()
        if collect:
            db.session.delete(collect)
            db.session.commit()
    #判断图片是否已收藏
    def has_collected(self, photo):
        if len(self.collections) == 0:
            return False
        collected_ids = []
        for collect in self.collections:
            collected_ids.append(collect.collected_id)
        index = 0
        try:
            index = collected_ids.index(photo.id)
        except ValueError:
            index = -1
        if index >= 0:
            return True
        else:
            return False
    #是否已关注某个用户
    def is_following(self, user):
        return self.following.filter_by(followed_id=user.id).first() is not None
    #是否被某个用户关注
    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None
    #关注
    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower=self,followed=user)
            db.session.add(follow)
            db.session.commit()
    #取消关注
    def unfollow(self, user):
        follow = self.following.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()
'''
    登录履历
'''
class Login(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)     #登录时间
    user_id = db.Column(db.String(32), db.ForeignKey('user.id'))                #登录账号
    user = db.relationship('User', back_populates='logins')                     #登录人员(反向关联)

'''
    图片信息
'''
class Photo(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)     #上传时间
    description = db.Column(db.String(500))                         #图片描述
    file_name = db.Column(db.String(64))                            #原图文件名
    file_name_s = db.Column(db.String(64))                          #缩略图文件名
    file_name_m = db.Column(db.String(64))                          #中等图文件名
    flag = db.Column(db.Integer)                                    #举报次数
    star = db.Column(db.Integer)                                    #点赞次数
    comments = db.relationship('Comment', back_populates='photo')   #图片评论
    tags = db.relationship('Tag', secondary=photos_tags, back_populates='photos')#图片标签
    author_id = db.Column(db.String(32), db.ForeignKey('user.id'))  #上传人ID(外键)
    author = db.relationship('User', back_populates='photos')       #上传人(反向关联)
    collectors = db.relationship('Collect', back_populates='collected', cascade='all')#收藏人
#图片数据删除后,执行图片文件删除
@db.event.listens_for(Photo, 'after_delete', named=True)
def delete_photo(**kwargs):
    target = kwargs['target']
    for file_name in [target.file_name, target.file_name_s, target.file_name_m]:
        if file_name is not None:
            file = os.path.join(current_app.config['SYS_FILE_UPLOAD_PATH'], file_name)
            if os.path.exists(file):
                os.remove(file)
'''
    图片评论
'''
class Comment(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)     #评论时间
    content = db.Column(db.Text)                                    #评论内容
    photo_id = db.Column(db.String(32), db.ForeignKey('photo.id'))  #图片ID(外键)
    photo = db.relationship('Photo', back_populates='comments')     #图片(反向关联)
'''
    图片标签
'''
class Tag(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(30), index = True)                                   #标签名称
    photos = db.relationship('Photo', secondary=photos_tags, back_populates='tags') #关联图片
'''
    图片收藏(收藏者和被收藏图片多对多关系映射)
'''
class Collect(db.Model):
    collector_id = db.Column(db.String(32), db.ForeignKey('user.id'), primary_key=True)     #收藏人ID
    collector = db.relationship('User', back_populates='collections', lazy='joined')        #收藏人
    collected_id = db.Column(db.String(32), db.ForeignKey('photo.id'),primary_key=True)     #被收藏图片ID
    collected = db.relationship('Photo', back_populates='collectors', lazy='joined')        #被收藏图片
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)                             #收藏时间