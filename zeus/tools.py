'''
    系统工具函数
'''
from flask import request, redirect, url_for
import time
from urllib.parse import urlparse,urljoin
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
def redirect_back(default='zeus.index', **kwargs):
    target = request.args.get('next')
    if target and is_safe_url(target):
        return redirect(target)
    return redirect(url_for(default, **kwargs))