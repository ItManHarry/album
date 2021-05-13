from flask import Flask,render_template
from flask_wtf.csrf import CSRFError
from zeus.settings import config
from zeus.extensions import bootstrap,moment,mail,ckeditor,db,migrate,csrf#,login_manager
def create_app(config_name=None):
    if config_name == None:
        config_name = 'dev_config'
    print('System configuration is : %s' %config_name)
    #创建实例
    app = Flask('zeus')
    #加载配置
    app.config.from_object(config[config_name])
    #注册系统扩展等
    register_web_extensions(app)
    register_web_global_path(app)
    register_web_global_context(app)
    register_web_errors(app)
    return app
#注册扩展组件
def register_web_extensions(app):
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    ckeditor.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    #login_manager.init_app(app)
    csrf.init_app(app)
#配置全局路径
def register_web_global_path(app):
    @app.route('/startup')
    def startup():
        return '<h1>System startup ...</h1>'
#注册全局变量/函数
def register_web_global_context(app):
    from zeus.tools import get_time
    @app.context_processor
    def make_template_context():
        return dict(get_time=get_time)
#配置错误页面跳转
def register_web_errors(app):
    @app.errorhandler(400)
    def request_invalid(e):
        return render_template('errors/400.html'), 400
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    @app.errorhandler(500)
    def inner_error(e):
        return render_template('errors/500.html'), 500
    @app.errorhandler(CSRFError)
    def csrf_error(e):
        return render_template('errors/csrf.html')