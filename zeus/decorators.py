from flask import Markup, flash, url_for, redirect,abort
from functools import wraps
from flask_login import current_user
'''
    拦截未激活用户
'''
def active_required(function):
    @wraps(function)
    def decorator_function(*args, **kwargs):
        if not current_user.active:
            message = Markup('''
                Please active your account first!
                Not receive the mail?
                <a href = '%s'>Resend the confirm mail</a>
            ''' % url_for('auth.resend_confirm_email'))
            flash(message)
            return redirect(url_for('main.index'))
        return function(*args, **kwargs)
    return decorator_function
'''
    拦截未授权用户
'''
def permission_required(permission_name):
    def decorator(function):
        @wraps(function)
        def decorated_function(*args, **kwargs):
            if not current_user.permitted(permission_name):
                abort(403)
            return function(*args, **kwargs)
        return decorated_function
    return decorator
'''
    拦截非管理员用户
'''
def admin_required(function):
    return permission_required('ADMINISTRATOR')(function)