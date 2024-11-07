"""
Musicatri启动入口模块
"""

from flask import Flask  # 导入Flask
from flask_injector import FlaskInjector
from injector import Injector

from service.abs.permission_service import PermissionService
from utils.locale import default_locale as _
from utils import default_config, log, DefaultConfigTag

dev_mode = False                            # dev mode
flask_app = Flask(__name__)                 # flak app

# 生命周期函数
def main():
    """ 创建Flask app，并执行生命周期函数 """
    global dev_mode
    global flask_app

    init_config()                   # 配置文件初始化
    init_cors()                     # 初始化cors
    init_exception_handler()        # 初始化异常处理器
    init_lifecycle()                # 初始化生命事件钩子
    init_flasgger()                 # 初始化接口文档
    init_blueprint()                # 初始化蓝图
    # init_database()                 # 初始化数据库

    init_container()                # 初始化容器
    print_banner()                  # 打印旗帜
    run_server()                    # 初始化socketio，启动项目

def init_container():
    """
    初始化flask injector，实现依赖注入
    """
    # 默认容器
    from container.context import ApplicationContext
    base_injector = Injector()
    base_injector.binder.install(ApplicationContext())
    FlaskInjector(app=flask_app, injector=base_injector)

def init_config():
    """
    配置文件初始化，将配置从.env文件以及config.json配置文件加载进入项目当中
    """
    # 检测是否处于开发者模式，在开发者模式下打印日志显示
    global dev_mode
    dev_mode = default_config.get(DefaultConfigTag.DEV_MODE)
    if dev_mode: log.warning(_("development mode is on, know more about development mode at README.md"))

def init_cors():
    """
    跨域配置初始化，进行跨域相关的配置，项目采用前后端分离架构，因此需要匹配适当的跨域政策来实现前后端跨域访问
    """
    from config import cors_configure
    cors_configure(flask_app, dev_mode=dev_mode)

def init_flasgger():
    """
    初始化项目接口文档(flasgger)，在开发者模式下，这份接口文档站点将会被禁用注册
    """
    if not dev_mode: return  # 仅在开发者模式下开启swagger文档
    from config import swagger_docs_configure
    swagger_docs_configure(flask_app)

def init_exception_handler():
    """
    初始化项目异常处理器，用于捕获全局异常来避免在生产环境下异常抛出，在开发者模式下异常处理器会被
    禁止注册，这是为了更好的堆栈轨迹显示，避免在开发阶段无法定位问题
    """
    if dev_mode: return
    from config import exception_handler_configure
    exception_handler_configure(flask_app)

def init_lifecycle():
    """
    初始化flask app生命周期事件，例如接受请求前等配置
    """
    from config import lifecycle_configuration
    lifecycle_configuration.lifecycle_configure(flask_app)

def run_server():
    """
    初始化socketio，注册项目socketio相关的命名空间，从而支持socketio相关功能
    返回WSGI(Web Server Gateway Interface)，代替原先的flask调试服务作为服务器
    """
    from sockets import socketio
    socketio.init_app(flask_app)

    if dev_mode: log.info(f"using: {socketio.async_mode}")

    host = default_config.get(DefaultConfigTag.SERVER_HOST)  # 服务器主机名
    port = default_config.get(DefaultConfigTag.SERVER_PORT)  # 服务器端口号

    # 同flask一样，使用injector时不建议启用
    log.info(_("musicatri launch successfully"))
    # 开发模式下有wsgi自己的地址绑定回显，不需要额外打印
    if not dev_mode: log.info(_("service listening on: http://%(host)s:%(port)s") % dict(host=host, port=port))

    socketio.run(app=flask_app, host=host, port=port, debug=False, log_output=dev_mode)
    log.info(_("musicatri teardown"))

def init_blueprint():
    """
    蓝图初始化，即初始化路由，路由中绝大多数接口使用RESTFUL风格编写，除开小部分静态资源接口开外
    """
    from controller import system_bp, static_bp, atri_bp, auth_bp, test_bp
    flask_app.register_blueprint(system_bp)  # system接口
    flask_app.register_blueprint(static_bp)  # static接口
    flask_app.register_blueprint(atri_bp)  # atri接口
    flask_app.register_blueprint(auth_bp)  # oauth接口

    # 仅开发者模式下注册测试接口
    if dev_mode: flask_app.register_blueprint(test_bp)

def init_database():
    """
    数据库初始化，对于部分库表，启动时需要检查库表数据状态，当数据状态出现问题时进行修复
    """
    from container import services
    try:
        services.get(PermissionService)  # 初始化权限相关数据库
    except Exception as error:
        log.error(_("Failed in connecting database : %(error)s") % {'error': error})
        exit(1)  # 数据库连接失败

def print_banner():
    """ 打印musicatri旗帜，好康的旗帜 """
    if default_config.get(DefaultConfigTag.PRINT_BANNER):
        log.info("""
    ______  ___                _____                _____         _____ 
    ___   |/  /____  _____________(_)_____________ ___  /____________(_)
    __  /|_/ / _  / / /__  ___/__  / _  ___/_  __ `/_  __/__  ___/__  / 
    _  /  / /  / /_/ / _(__  ) _  /  / /__  / /_/ / / /_  _  /    _  /  
    /_/  /_/   \__,_/  /____/  /_/   \___/  \__,_/  \__/  /_/     /_/   """)

if __name__ == '__main__':
    # 注: Debug模式下默认重载两次，请不要使用Debug模式运行，Debug会导致Flask Injection出现错误
    main()

