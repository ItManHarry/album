'''
    系统配置
'''
import os
#开发数据库
dev_db = os.getenv('DEVELOP_DB')
#生产数据库
pro_db = os.getenv('PRODUCT_DB')
#全局配置
class GlobalSetting():
    SECRET_KEY = os.getenv('SECRET_KEY', '123456789qwertyuiop!@$%asdfgh')   #秘钥 session用
    BOOTSTRAP_SERVE_LOCAL = True                                            #Bootstrap本地化
    ITEM_COUNT_PER_PAGE = 10                                                #分页显示:每页的数量
    MAIL_SERVER = 'smtp.qq.com'                                             #邮箱服务器
    MAIL_PORT=465                                                           #服务器端口
    MAIL_USE_SSL=True                                                       #使用SSL
    MAIL_USE_TLS=False                                                      #禁用TLS
    MAIL_USERNAME='280688074@qq.com'                                        #邮箱账号
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')                                #邮箱授权码
    MAIL_DEFAULT_SENDER = ('Harry.Cheng', '280688074@qq.com')               # 默认发件人
    MAIL_SUJECT_PREFIX = '[Album]'
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