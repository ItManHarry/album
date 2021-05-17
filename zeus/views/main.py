from flask import Blueprint, render_template
from flask_login import login_required
from zeus.decorators import active_required
bp_main = Blueprint('main', __name__)
#首页
@bp_main.route('/index')
def index():
    return render_template('main/index.html')
#图片上传
@bp_main.route('/upload')
@login_required
@active_required
def upload():
    return render_template('main/upload.html')