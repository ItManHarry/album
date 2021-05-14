from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from zeus.extensions import mail
#异步发送邮件
def async_send_mail(app, message):
    with app.app_context():
        mail.send(message)
#发送邮件
def send_mail(to, subject, template, **kwargs):
    message = Message(current_app.config['MAIL_SUJECT_PREFIX'] + subject, recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    app = current_app._get_current_object()
    thread = Thread(target=async_send_mail, args=[app, message])
    thread.start()
    return thread
#发送账号激活邮件
def active_account_email(user, token, to=None):
    send_mail(to=to or user.email, subject='账号激活', template='emails/confirm', user=user, token=token)
#密码重置邮件
def reset_password_email(user, token):
    send_mail(subject='密码重置', to=user.email, template='emails/reset_password', user=user, token=token)
#更换邮件邮件
def change_email_email(user, token, to=None):
    send_mail(subject='更改邮箱', to=to or user.email, template='emails/change_email', user=user, token=token)