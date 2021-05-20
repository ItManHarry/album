import os.path
from flask import Blueprint, render_template,current_app,request,send_from_directory,redirect,url_for
from flask_login import login_required,current_user
from flask_dropzone import random_filename
import uuid
from zeus.extensions import db
from zeus.models import Photo
from zeus.decorators import active_required,permission_required
from zeus.tools import resize_image
bp_main = Blueprint('main', __name__)
#首页
@bp_main.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['HOME_PHOTO_COUNT_PER_PAGE']
    pagination = Photo.query.order_by(Photo.timestamp.desc()).paginate(page, per_page)
    photos = pagination.items
    return render_template('main/index.html', photos=photos, pagination=pagination)
#图片上传
@bp_main.route('/upload', methods=['GET','POST'])
@login_required                   #是否登录
@active_required                  #账号是否激活
@permission_required('UPLOAD')    #是否具备上传权限
def upload():
    if request.method == 'POST' and 'file' in request.files:
        f = request.files.get('file')                                               #获取文件
        filename = random_filename(f.filename)                                      #重新生成文件名
        f.save(os.path.join(current_app.config['SYS_FILE_UPLOAD_PATH'], filename))  #执行上传
        file_name_s = resize_image(f, filename, 400)
        file_name_m = resize_image(f, filename, 800)
        photo = Photo(
            id=uuid.uuid4().hex,
            file_name=filename,
            file_name_s = file_name_s,
            file_name_m = file_name_m,
            author = current_user._get_current_object()
        )
        db.session.add(photo)
        db.session.commit()
    return render_template('main/upload.html')
#显示头像(For Image_Src)
@bp_main.route('/avatar/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)
#显示图片(For Image_Src)
@bp_main.route('/photo/<path:filename>')
def get_photo(filename):
    return send_from_directory(current_app.config['SYS_FILE_UPLOAD_PATH'], filename)
'''
    查看图片
    from_path:点击来源(主页/个人中心)
    photo_id:图片ID
'''
@bp_main.route('/photo/show/<from_path>/<photo_id>')
def show_photo(from_path, photo_id):
    photo = Photo.query.get_or_404(photo_id)
    author = photo.author
    # 获取所有的图片
    if from_path == 'home':             #主页点击则获取所有用户上传的图片
        ids = get_all_photo_ids()
    if from_path == 'personal':         #个人中心点击则获取当前用户上传的所有图片
        ids = get_all_photo_ids(photo.author)
    photo_index = ids.index(photo_id)
    sign = ''   #标识是否是第一张或最后一张
    if photo_index == 0:
        sign = 'first'
    if photo_index == len(ids)-1:
        sign = 'last'
    return render_template('main/photo.html', photo=photo, sign=sign, user=author, from_path=from_path)
'''
    上一张/下一张图片
    from_path:点击来源(主页/个人中心)
    sign:切换标识(上一页:previous,下一页:next)
    photo_id:图片ID
'''
@bp_main.route('/photo/<from_path>/<sign>/<photo_id>')
def switch_photo(from_path, sign, photo_id):
    current_photo = Photo.query.get_or_404(photo_id)
    # 获取所有的图片ID
    if from_path == 'home':  # 主页点击则获取所有用户上传的图片
        ids = get_all_photo_ids()
    if from_path == 'personal':  # 个人中心点击则获取当前用户上传的所有图片
        ids = get_all_photo_ids(current_photo.author)
    current_photo_index = ids.index(photo_id)
    #上一张
    if sign == 'previous' and current_photo_index != 0:
        photo_id = ids[current_photo_index-1]
    #下一张
    if sign == 'next' and current_photo_index != len(ids)-1:
        photo_id = ids[current_photo_index+1]
    return redirect(url_for('.show_photo', from_path=from_path, photo_id=photo_id))
#获取当前用户所有图片ID
def get_all_photo_ids(author=None):
    if author is None:  #获取所有用户上传的图片
        photos = Photo.query.order_by(Photo.timestamp.desc()).all()
    else:               #获取当前用户上传的图片
        photos = Photo.query.with_parent(author).order_by(Photo.timestamp.desc()).all()
    ids = []
    for photo in photos:
        ids.append(photo.id)
    print('Photo count is  : ', len(ids))
    return ids