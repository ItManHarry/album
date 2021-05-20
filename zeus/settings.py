'''
    系统配置
'''
import os
#开发数据库
dev_db = os.getenv('DEVELOP_DB')
#生产数据库
pro_db = os.getenv('PRODUCT_DB')
#基础路径
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
#全局配置
class GlobalSetting():
    SECRET_KEY = os.getenv('SECRET_KEY', '123456789qwertyuiop!@$%asdfgh')   #秘钥 session用
    BOOTSTRAP_SERVE_LOCAL = True                                            #Bootstrap本地化
    ITEM_COUNT_PER_PAGE = 10                                                #表格分页显示:每页的数量
    PHOTO_COUNT_PER_PAGE = 12                                               #图片分页显示:每页的数量(个人中心)
    HOME_PHOTO_COUNT_PER_PAGE = 24                                          # 图片分页显示:每页的数量(网址首页)
    MAIL_SERVER = 'smtp.qq.com'                                             #邮箱服务器
    MAIL_PORT = 465                                                         #服务器端口
    MAIL_USE_SSL = True                                                     #使用SSL
    MAIL_USE_TLS = False                                                    #禁用TLS
    MAIL_USERNAME = '280688074@qq.com'                                      #邮箱账号
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')                              #邮箱授权码
    MAIL_DEFAULT_SENDER = ('Harry.Cheng', '280688074@qq.com')               #默认发件人
    MAIL_SUBJECT_PREFIX = '[Album]'                                         #邮件Title前缀
    SYS_FILE_UPLOAD_PATH = os.path.join(basedir, 'uploads')                 #文件上传路径
    DROPZONE_MAX_FILE_SIZE = 3                                              #Dropzone上传文件大小(3M)
    DROPZONE_MAX_FILES = 30                                                 #Dropzone上传文件最大数量
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024                                    #Flask内置文件上传大小设置
    DROPZONE_ALLOWED_FILE_TYPE = 'image'                                    #Dropzone允许上传的文件类型
    DROPZONE_ENABLE_CSRF = True                                             #Dropzone上传启用CSRF令牌验证
    #以下为Dropzone错误消息提示
    DROPZONE_INVALID_FILE_TYPE = '上传文件类型错误！！！'
    DROPZONE_FILE_TOO_BIG = '上传文件超过最大限制！！！'
    DROPZONE_SERVER_ERROR = '服务端错误!!!'
    DROPZONE_BROWSER_UNSUPPORTED = '浏览器不支持！！！'
    DROPZONE_MAX_FILE_EXCEED = '超出最大文件上传数量！！！'
    ALBUM_IMG_SIZE = {'small': 400, 'medium': 800}                          #图片裁剪尺寸
    ALBUM_IMG_SUFFIX = {
        ALBUM_IMG_SIZE['small']: '_s',  #缩略图
        ALBUM_IMG_SIZE['medium']: '_m'  #中等图
    }
    AVATARS_SAVE_PATH = os.path.join(SYS_FILE_UPLOAD_PATH, 'avatars')       #头像存储路径
    AVATARS_SIZE_TUPLE = (24,100,200)                                       #头像尺寸
class DevelopSetting(GlobalSetting):
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DEVELOP_DATABASE_URL', dev_db)
class ProductSetting(GlobalSetting):
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('PRODUCT_DATABASE_URL', pro_db)
#配置映射
config = {
    'dev_config':DevelopSetting,
    'pro_config':ProductSetting
}
operations = {
    'confirm':'confirm',
    'reset_password':'reset_password',
    'change_email':'change_email'
}