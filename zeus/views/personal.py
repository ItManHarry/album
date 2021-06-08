from flask import Blueprint, render_template,url_for,redirect
from flask_login import login_required,current_user
bp_personal = Blueprint('personal', __name__)
'''
    个人设置
'''
@bp_personal.route('/setting/profile')
@login_required
def profile():
    return render_template('user/setting/base.html', user=current_user)