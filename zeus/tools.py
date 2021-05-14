'''
    系统工具函数
'''
from flask import request, redirect, url_for, current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadSignature, SignatureExpired
import time
from urllib.parse import urlparse,urljoin
from zeus.settings import operations
from zeus.extensions import db
#获取当前时间
def get_time():
    return 'Now is : %s' %time.strftime('%Y年%m月%d日')
#判断地址是否安全
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http','https') and ref_url.netloc == test_url.netloc
'''
    通用返回方法
    默认返回博客首页
'''
def redirect_back(default='main.index', **kwargs):
    target = request.args.get('next')
    if target and is_safe_url(target):
        return redirect(target)
    return redirect(url_for(default, **kwargs))
'''
    生成令牌-邮件验证
'''
def generate_token(user, operation, expire_in = None, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)
    data = dict(id=user.id, operation=operation)
    data.update(**kwargs)
    return s.dumps(data)
'''
    验证令牌
'''
def validate_token(user, token, operaion):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except(BadSignature, SignatureExpired):
        return False
    if operaion != data.get('operation') or user.id != data.get('id'):
        return False
    if operaion == operations['confirm']:
        user.active = True  #验证通过激活用户
    else:
        return False
    db.session.commit()
    return True