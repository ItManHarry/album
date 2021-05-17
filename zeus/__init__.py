from flask import Flask,render_template
from flask_wtf.csrf import CSRFError
from zeus.settings import config
from zeus.extensions import bootstrap,moment,mail,ckeditor,db,migrate,csrf,login_manager
import click
import uuid
#创建Flask实例
def create_app(config_name=None):
    if config_name == None:
        config_name = 'dev_config'
    #print('System configuration is : %s' %config_name)
    #创建实例
    app = Flask('zeus')
    #加载配置
    app.config.from_object(config[config_name])
    #注册系统扩展等
    register_web_extensions(app)
    register_web_global_path(app)
    register_web_global_context(app)
    register_web_errors(app)
    register_web_views(app)
    register_web_shell(app)
    register_web_command(app)
    return app
#注册扩展组件
def register_web_extensions(app):
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    ckeditor.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
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
#注册系统各个功能模块
def register_web_views(app):
    from zeus.views.auth import bp_auth
    from zeus.views.main import bp_main
    app.register_blueprint(bp_auth, url_prefix='/auth')
    app.register_blueprint(bp_main, url_prefix='/main')
#注册shell环境
def register_web_shell(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)
#注册自定义命令
def register_web_command(app):
    #初始化系统
    @app.cli.command()
    @click.option('--username', prompt=True, help='用户账号.')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True,help='用户密码.')
    def init(username, password):
        from zeus.models import User
        click.echo('执行数据库初始化......')
        db.create_all()
        click.echo('数据库初始化完成！！！')
        click.echo('创建默认用户')
        user = User.query.first()
        if user:
            click.echo('已存在用户,跳过创建......')
        else:
            click.echo('执行创建默认用户......')
            user = User(
                id = uuid.uuid4().hex,
                code=username,
                name = 'admin',
                email = 'xxx@xxx.xxx',
                website = 'http://xxx.xxx',
                bio = 'xxx',
                location = 'xxx-xxx-xxx',
                active=True
            )
            user.set_password(password)
            db.session.add(user)
        db.session.commit()
        click.echo('系统初始化完成......')