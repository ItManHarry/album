import os.path, uuid
from flask import Blueprint, render_template,current_app,request,send_from_directory,redirect,url_for,flash
from flask_login import login_required,current_user
from flask_dropzone import random_filename
from zeus.extensions import db
from zeus.models import Photo, Comment,Tag, Collect
from zeus.forms.main import PhotoForm, PhotoCommentForm, PhotoTagForm
from zeus.decorators import active_required,permission_required
from zeus.tools import resize_image,redirect_back
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
            star = 0,
            flag = 0,
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
@bp_main.route('/photo/show/<from_path>/<photo_id>/<nav_id>', methods=['GET','POST'])
def show_photo(from_path, photo_id, nav_id):
    photo = Photo.query.get_or_404(photo_id)
    author = photo.author
    # 获取所有的图片
    if from_path == 'home':             #主页点击则获取所有用户上传的图片
        ids = get_all_photo_ids()
    if from_path == 'personal':         #个人中心点
        ids = get_all_photo_ids(current_user, nav_id)
    photo_index = ids.index(photo_id)
    sign = ''                           #标识是否是第一张或最后一张
    if photo_index == 0:
        sign = 'first'
    if photo_index == len(ids)-1:
        sign = 'last'
    '''
        执行数据保存
    '''
    desc_form = PhotoForm()             #描述表单
    tag_form = PhotoTagForm()           #标签表单
    if from_path == 'personal' and request.method == 'GET':
        desc_form.description.data = photo.description
    comm_form = PhotoCommentForm()      # 评论表单
    if from_path == 'home' and comm_form.validate_on_submit():
        comment = Comment(
            id=uuid.uuid4().hex,
            content=comm_form.content.data,
            photo_id=photo_id
        )
        db.session.add(comment)
        db.session.commit()
        flash('评论发表成功!!!')
        return redirect(url_for('.show_photo', from_path=from_path, photo_id=photo_id, nav_id=nav_id))
    if from_path == 'personal' and desc_form.validate_on_submit():
        photo.description = desc_form.description.data
        db.session.commit()
        flash('描述保存成功!!!')
        return redirect(url_for('.show_photo', from_path=from_path, photo_id=photo_id, nav_id=nav_id))
    if from_path == 'personal' and tag_form.validate_on_submit():
        for name in tag_form.tag.data.split(' '):
            tag = Tag.query.filter_by(name=name.strip()).first()
            if tag is None:
                tag = Tag(id=uuid.uuid4().hex,name=name.strip())
                db.session.add(tag)
                db.session.commit()
            if tag not in photo.tags:   #没有关联的进行关联
                photo.tags.append(tag)
                db.session.commit()
        flash('标签保存成功!!!')
        return redirect(url_for('.show_photo', from_path=from_path, photo_id=photo_id,nav_id=nav_id))
    return render_template('main/photo.html', photo=photo, sign=sign, user=author, from_path=from_path, nav_id=nav_id, desc_form=desc_form, comm_form=comm_form, comments=photo.comments, tag_form=tag_form, tags=photo.tags)
'''
    删除标签
'''
@bp_main.route('/photo/tag/<photo_id>/<tag_id>', methods=['POST'])
def del_tag(photo_id, tag_id):
    photo = Photo.query.get_or_404(photo_id)
    tag = Tag.query.get_or_404(tag_id)
    photo.tags.remove(tag)
    db.session.commit()
    if not tag.photos:
        db.session.delete(tag)
        db.session.commit()
    flash('标签已移除!!!')
    return redirect(url_for('.show_photo', from_path='personal', photo_id=photo_id))
'''
    上一张/下一张图片
    from_path:点击来源(主页/个人中心)
    sign:切换标识(上一页:previous,下一页:next)
    photo_id:图片ID
'''
@bp_main.route('/photo/<from_path>/<sign>/<photo_id>/<nav_id>')
def switch_photo(from_path, sign, photo_id,nav_id):
    # 获取所有的图片ID
    if from_path == 'home':  # 主页点击则获取所有用户上传的图片
        ids = get_all_photo_ids()
    if from_path == 'personal':  # 个人中心点击则获取当前用户上传的所有图片
        ids = get_all_photo_ids(current_user, nav_id)
    current_photo_index = ids.index(photo_id)
    #上一张
    if sign == 'previous' and current_photo_index != 0:
        photo_id = ids[current_photo_index-1]
    #下一张
    if sign == 'next' and current_photo_index != len(ids)-1:
        photo_id = ids[current_photo_index+1]
    return redirect(url_for('.show_photo', from_path=from_path, photo_id=photo_id,nav_id=nav_id))
#点赞图片
@bp_main.route('/photo/star/<photo_id>')
def star_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    stars = 0 if photo.star == None else photo.star
    photo.star = stars + 1
    db.session.commit()
    return redirect_back()
#举报图片
@bp_main.route('/photo/report/<photo_id>')
def report_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    flags = 0 if photo.flag == None else photo.flag
    photo.flag = flags + 1
    db.session.commit()
    return redirect_back()
'''
    获取图片ID
    author:默认None获取主页所有的图片,即所有用户上传的图片,
    不为None表示个人中心的图片
    nav:表示个人中心点击个人相册还是已收藏图片(photos:相册 collects:已收藏)
'''
def get_all_photo_ids(user=None,nav=None):
    if user is None:  #获取所有用户上传的图片
        photos = Photo.query.order_by(Photo.timestamp.desc()).all()
    else:               #获取当前用户上传的图片
        if nav == 'photos':
            photos = Photo.query.with_parent(user).order_by(Photo.timestamp.desc()).all()
        if nav == 'collects':
            collects = Collect.query.with_parent(user).all()
            photo_ids = []
            for collect in collects:
                photo_ids.append(collect.collected_id)
            #print('Photo ids : ', photo_ids)
            photos = Photo.query.filter(Photo.id.in_(photo_ids)).order_by(Photo.timestamp.desc()).all()
    ids = []
    for photo in photos:
        ids.append(photo.id)
    print('Photo count is  : ', len(ids))
    return ids