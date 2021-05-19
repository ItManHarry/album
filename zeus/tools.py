'''
    系统工具函数
'''
from flask import request, redirect, url_for, current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadSignature, SignatureExpired
import time
from urllib.parse import urlparse,urljoin
from zeus.settings import operations
from zeus.extensions import db
import PIL
from PIL import Image
import os
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
def validate_token(user, token, operation, new_password=None):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except(BadSignature, SignatureExpired):
        return False
    if operation != data.get('operation') or user.id != data.get('id'):
        return False
    if operation == operations['confirm']:
        user.active = True                          #验证通过激活用户
    elif operation == operations['reset_password']:
        user.set_password(new_password)             #重置密码
    else:
        return False
    db.session.commit()
    return True
'''
    图片裁剪    
'''
def resize_image(image, file_name, base_width):
    file_name, ext = os.path.splitext(file_name) #获取文件名和文件扩展名
    img = Image.open(image)
    if img.size[0] <= base_width:
        return file_name + ext
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
    file_name += current_app.config['ALBUM_IMG_SUFFIX'][base_width] + ext
    img.save(os.path.join(current_app.config['SYS_FILE_UPLOAD_PATH'], file_name), optimize=True, quality=85)
    return file_name