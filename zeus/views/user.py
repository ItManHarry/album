from flask import Blueprint, request, render_template, current_app,redirect,url_for,jsonify
from flask_login import login_required, current_user
from zeus.models import User, Photo, Collect
from zeus.extensions import db
from zeus.tools import redirect_back
from zeus.decorators import active_required, permission_required
bp_user = Blueprint('user', __name__)
'''
    个人中心
'''
@bp_user.route('/index/<user_code>')
def index(user_code):
    user = User.query.filter_by(code=user_code).first_or_404()
    followings = []
    for follow in user.following:
        followings.append(follow.followed)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['PHOTO_COUNT_PER_PAGE']
    pagination = Photo.query.with_parent(user).order_by(Photo.timestamp.desc()).paginate(page, per_page)
    photos = pagination.items
    return render_template('user/index.html', user=user, photos=photos, pagination=pagination, from_path='personal', nav_id='photos', followings=followings)
'''
    图片删除
'''
@bp_user.route('/photo/delete/<photo_id>', methods=['POST'])
def delete(photo_id):
    from zeus.views.main import get_all_photo_ids
    photo = Photo.query.get_or_404(photo_id)
    author = photo.author
    ids = get_all_photo_ids(author)
    # 被删除图片index
    index = ids.index(photo_id)
    '''
        此处做出判断:
            1. 如果当前删除的是最后一张照片,删除后跳转至前一张照片
            2. 否则跳转至下一张照片
    '''
    if index == len(ids)-1:
        photo_id = ids[index-1]
    else:
        photo_id = ids[index+1]
    # 执行删除
    db.session.delete(photo)
    db.session.commit()
    # 重新获取图片数量,如果已全部删除,则跳转值至个人中心
    ids = get_all_photo_ids(author)
    if len(ids) == 0:
        return redirect(url_for('.index', user_code=photo.author.code))
    return redirect(url_for('main.show_photo', from_path='personal', photo_id=photo_id))
'''
    收藏图片
'''
@bp_user.route('/photo/collect/<photo_id>')
@login_required                   #是否登录
@active_required                  #账号是否激活
@permission_required('COLLECT')   #是否具备收藏权限
def collect(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    current_user.collect(photo)
    return redirect_back()
'''
    取消收藏
'''
@bp_user.route('/photo/uncollect/<photo_id>')
@login_required                   #是否登录
def uncollect(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    current_user.uncollect(photo)
    return redirect_back()
'''
    已收藏图片
'''
@bp_user.route('/photo/collect/list/<user_code>')
def collected_list(user_code):
    user = User.query.filter_by(code=user_code).first_or_404()
    followings = []
    for follow in user.following:
        followings.append(follow.followed)
    collects = Collect.query.with_parent(user).all()
    photo_ids = []
    for collect in collects:
        photo_ids.append(collect.collected_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['PHOTO_COUNT_PER_PAGE']
    pagination = Photo.query.filter(Photo.id.in_(photo_ids)).order_by(Photo.timestamp.desc()).paginate(page, per_page)
    photos = pagination.items
    return render_template('user/index.html', user=user, photos=photos, pagination=pagination, from_path='personal', nav_id='collects', followings=followings)
'''
    关注用户
'''
@bp_user.route('/user/follow/<user_id>')
@login_required                   #是否登录
@active_required                  #账号是否激活
@permission_required('FOLLOW')   #是否具备关注权限
def follow(user_id):
    user = User.query.get_or_404(user_id)
    current_user.follow(user)
    return redirect_back()
'''
    显示已关注用户清单
'''
@bp_user.route('/user/follow/<user_id>/list')
@login_required                   #是否登录
@active_required                  #账号是否激活
def follow_list(user_id):
    user = User.query.get_or_404(user_id)
    followings = []
    for follow in user.following:
        followings.append(follow.followed)
    print('Following Users are : ', followings)
    return render_template('user/index.html', user=user, photos=None, pagination=None, from_path='personal', nav_id='follow', followings=followings)
'''
    取消关注用户
'''
@bp_user.route('/user/unfollow/<user_id>')
@login_required                   #是否登录
@active_required                  #账号是否激活
def unfollow(user_id):
    user = User.query.get_or_404(user_id)
    current_user.unfollow(user)
    return redirect_back()
@bp_user.route('/user/info/<user_id>')
def info(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(name=user.name, code=user.code)