from flask import Blueprint, request, render_template, current_app
from zeus.models import User, Photo
bp_user = Blueprint('user', __name__)
#个人中心
@bp_user.route('/index/<user_code>')
def index(user_code):
    user = User.query.filter_by(code=user_code).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['PHOTO_COUNT_PER_PAGE']
    pagination = Photo.query.with_parent(user).order_by(Photo.timestamp.desc()).paginate(page, per_page)
    photos = pagination.items
    return render_template('user/index.html', user=user, photos=photos, pagination=pagination)