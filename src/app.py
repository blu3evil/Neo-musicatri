"""
Musicatri启动入口模块
"""
from flask import Flask  # 导入Flask
from service.base_service.permission_service import PermissionService
from utils.locale import default_locale as _
from utils import default_config, log, DefaultConfigTag

# 生命周期函数
def create_app() -> Flask:
    """ 创建Flask app，并执行生命周期函数 """
    app = Flask(__name__)                       # flak app
    dev_mode = init_config()                    # 配置文件初始化
    init_cors(app, dev_mode)                    # 初始化cors
    init_exception_handler(app, dev_mode)       # 初始化异常处理器
    init_lifecycle(app, dev_mode)               # 初始化生命事件钩子
    init_flasgger(app, dev_mode)                # 初始化接口文档
    init_blueprint(app, dev_mode)               # 初始化蓝图
    init_socketio(app, dev_mode)                # 初始化socketio
    init_database()                             # 初始化数据库

    print_banner()                              # 打印旗帜
    log.info(_("Musicatri run successfully"))
    return app  # 返回app实例

def init_config() -> bool:
    """ 配置文件初始化 """
    dev_mode = default_config.get(DefaultConfigTag.DEV_MODE)  # 开发者模式
    if dev_mode: log.warning(_("development mode is on, know more about development mode at README.md"))
    return dev_mode

def init_cors(app: Flask, dev_mode: bool):
    from config import cors_configure
    cors_configure(app, dev_mode=dev_mode)

def init_flasgger(app: Flask, dev_mode: bool):
    """ 初始化swagger文档 """
    if not dev_mode: return  # 仅在开发者模式下开启swagger文档
    from config import swagger_docs_configure
    swagger_docs_configure(app)

def init_exception_handler(app: Flask, dev_mode: bool):
    """ 初始化异常处理器 """
    if dev_mode: return
    from config import exception_handler_configure
    exception_handler_configure(app)

def init_lifecycle(app: Flask, dev_mode: bool):
    """ 初始化flask app生命周期事件 """
    from config import lifecycle_configuration
    lifecycle_configuration.lifecycle_configure(app)

def init_socketio(app: Flask, dev_mode: bool):
    """ 初始化socketio """
    from config import socketio_configure
    socketio_configure(app)

def init_blueprint(app: Flask, dev_mode: bool):
    """ 蓝图初始化（路由） """
    from controller import system_bp, static_bp, atri_bp, auth_bp, test_bp
    app.register_blueprint(system_bp)  # system接口
    app.register_blueprint(static_bp)  # static接口
    app.register_blueprint(atri_bp)  # atri接口
    app.register_blueprint(auth_bp)  # oauth接口

    # 仅开发者模式下注册测试接口
    if dev_mode: app.register_blueprint(test_bp)

def init_database():
    """ 数据库初始化 """
    from container import services
    try:
        services.get(PermissionService)  # 初始化权限相关数据库
    except Exception as error:
        log.error(_("Failed in connecting database : %(error)s") % {'error': error})
        exit(1)  # 数据库连接失败

def print_banner():
    """ 打印musicatri旗帜 """
    if default_config.get(DefaultConfigTag.PRINT_BANNER):
        log.info("""
    ______  ___                _____                _____         _____ 
    ___   |/  /____  _____________(_)_____________ ___  /____________(_)
    __  /|_/ / _  / / /__  ___/__  / _  ___/_  __ `/_  __/__  ___/__  / 
    _  /  / /  / /_/ / _(__  ) _  /  / /__  / /_/ / / /_  _  /    _  /  
    /_/  /_/   \__,_/  /____/  /_/   \___/  \__,_/  \__/  /_/     /_/   """)

if __name__ == '__main__':
    # 通过配置文件加载监听端口号和ip
    host = default_config.get(DefaultConfigTag.SERVER_HOST)
    port = default_config.get(DefaultConfigTag.SERVER_PORT)
    # 注: Debug模式下默认重载两次，请不要使用Debug模式运行，Debug会导致Flask Injection出现错误
    create_app().run(debug=False, host=host, port=port)
