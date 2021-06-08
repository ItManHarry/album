from flask import Blueprint, render_template,url_for,redirect,request
from flask_login import login_required,current_user
from zeus.forms.auth import RegisterForm
from zeus.extensions import db
bp_personal = Blueprint('personal', __name__)
'''
    个人设置
'''
@bp_personal.route('/setting/profile', methods=['GET','POST'])
@login_required
def profile():
    form = RegisterForm()
    if request.method == 'GET':
        form.code.data = current_user.code
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.website.data = current_user.website
        form.location.data = current_user.location
        form.birthday.data = current_user.birth
    if form.validate_on_submit():
        #current_user.code = form.code.data
        current_user.name = form.name.data
        #current_user.email = form.email.data
        current_user.website = form.website.data
        current_user.location = form.location.data
        current_user.birth = form.birthday.data
        db.session.commit()
        return redirect(url_for('.profile'))
    return render_template('user/setting/profile.html', form=form, user=current_user)