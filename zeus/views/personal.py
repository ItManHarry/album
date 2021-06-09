from flask import Blueprint, render_template, url_for, redirect, request, flash, current_app
from flask_login import login_required,current_user
from zeus.forms.personal import ProfileForm, AvatarForm, CropAvatarForm
from zeus.extensions import db, avatars
bp_personal = Blueprint('personal', __name__)
'''
    个人设置
'''
@bp_personal.route('/setting/profile', methods=['GET','POST'])
@login_required
def profile():
    form = ProfileForm()
    if request.method == 'GET':
        form.code.data = current_user.code
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.website.data = current_user.website
        form.location.data = current_user.location
        form.birthday.data = current_user.birth
    if form.validate_on_submit():
        current_user.code = form.code.data
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.website = form.website.data
        current_user.location = form.location.data
        current_user.birth = form.birthday.data
        db.session.commit()
        flash('信息保存成功!!!')
        return redirect(url_for('.profile'))
    return render_template('user/setting/profile.html', form=form, user=current_user)
'''
    上传自定义头像
'''
@bp_personal.route('/setting/avatar', methods=['GET','POST'])
@login_required
def avatar():
    upload_form = AvatarForm()
    crop_form = CropAvatarForm()
    return render_template('user/setting/avatar.html', user=current_user, upload_form=upload_form, crop_form=crop_form)
'''
    上传自定义头像
'''
@bp_personal.route('/setting/avatar/upload', methods=['POST'])
@login_required
def upload():
    form = AvatarForm()
    if form.validate_on_submit():
        image = form.image.data
        file_name = avatars.save_avatar(image)
        current_user.avatar_r = file_name
        db.session.commit()
        flash('头像上传成功, 请裁剪!!!')
    return redirect(url_for('.avatar'))
@bp_personal.route('/setting/avatar/crop', methods=['POST'])
@login_required
def crop():
    form = CropAvatarForm()
    if form.validate_on_submit():
        x = form.x.data
        y = form.y.data
        w = form.w.data
        h = form.h.data
        if current_user.avatar_r:
            filenames = avatars.crop_avatar(current_user.avatar_r, x, y, w, h)
        else:
            filenames = avatars.crop_avatar(current_user.avatar_l, x, y, w, h)
        current_user.avatar_s = filenames[0]
        current_user.avatar_m = filenames[1]
        current_user.avatar_l = filenames[2]
        db.session.commit()
        flash('头像更新成功!!!')
    return redirect(url_for('.avatar'))