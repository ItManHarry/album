import os.path
from flask import Blueprint, render_template,current_app,request
from flask_login import login_required,current_user
from flask_dropzone import random_filename
from zeus.extensions import db
from zeus.models import Photo
from zeus.decorators import active_required,permission_required
import uuid
bp_main = Blueprint('main', __name__)
#首页
@bp_main.route('/index')
def index():
    return render_template('main/index.html')
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
        photo = Photo(id=uuid.uuid4().hex,file_name=filename,author=current_user._get_current_object()) #保存记录
        db.session.add(photo)
        db.session.commit()
    return render_template('main/upload.html')