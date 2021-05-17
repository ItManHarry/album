from flask import Markup, flash, url_for, redirect
from functools import wraps
from flask_login import current_user
'''
    拦截未激活账号
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