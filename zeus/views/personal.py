from flask import Blueprint, render_template, url_for, redirect, request, flash, current_app, jsonify
from flask_login import login_required,current_user
from zeus.forms.personal import ProfileForm, AvatarForm, CropAvatarForm
from zeus.extensions import db, avatars
from sqlalchemy import text
from zeus.models import Notification
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
    sql = '''
        select id, code, name from user where code = '%(code)s'
    ''' % {'code': '20112004'}
    ts = text('select id, code, name from user where code = :code')
    #results = db.session.execute(sql)
    results = db.session.execute(ts, {'code': '20112004'})
    print('Result is : >>>>>>>>>>>>>>>>>>>', results)
    for result in results:
        print('Result data is : ', result)
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
'''
    消息管理
'''
@bp_personal.route('/setting/notice/list')
@login_required                   #是否登录
def notice_list():
    notices = Notification.query.with_parent(current_user).order_by(Notification.timestamp.desc()).all()
    return render_template('user/setting/notices.html', notices=notices, user=current_user)
'''
    查看消息
'''
@bp_personal.route('/setting/notice/show/<notice_id>')
def notice_show(notice_id):
    notice = Notification.query.get_or_404(notice_id)
    if not notice.is_read:
        notice.is_read = True
        db.session.commit()
    return jsonify(message=notice.message)
'''
    删除消息
'''
@bp_personal.route('/setting/notice/delete/<notice_id>')
@login_required
def notice_delete(notice_id):
    notice = Notification.query.get_or_404(notice_id)
    db.session.delete(notice)
    db.session.commit()
    return redirect(url_for('.notice_list', user_id=current_user.id))