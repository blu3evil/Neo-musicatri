"""
Musicatri启动入口模块
"""
import os
from datetime import timedelta
from os import path

from flask import Flask, request, g, jsonify, Response
from flask_caching import Cache
from flask_injector import FlaskInjector
from flask_session import Session
from injector import Injector

import utils.middlewares
from utils import default_config, log, DefaultConfigTag
from utils.locale import default_locale as _, locales
from utils import config, ConfigEnum

dev_mode = False                                                        # dev mode
root_path = path.dirname(path.dirname(path.abspath(__file__)))          # root path
log.debug(f'musicatri root path: {root_path}')

app = Flask(__name__)                                                   # flak app
cache = Cache()
session = Session()

# 生命周期函数
def main():
    """ 创建Flask app，并执行生命周期函数 """
    init_config()  # 配置文件初始化
    init_cors()  # 初始化cors

    init_exception_handler()        # 初始化异常处理器
    init_lifecycle()                # 初始化生命事件钩子
    init_flasgger()                 # 初始化接口文档
    init_views()                    # 初始化蓝图
    init_database()                 # 初始化数据库

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
    FlaskInjector(app=app, injector=base_injector)

def init_config():
    """ 配置文件初始化 """
    global dev_mode
    dev_mode = config.get(ConfigEnum.APP_DEV_MODE)
    if dev_mode: log.warning(_("development mode is on, know more about development mode at README.md"))

    app.config['SECRET_KEY'] = config.get(ConfigEnum.APP_SECURITY_SECRET_KEY)

    # ============================================== OAUTH =============================================================
    # oauth2开启https
    if config.get(ConfigEnum.APP_SECURITY_OAUTH_INSECURE_TRANSPORT):
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # 允许oauth2动态权限调整
    if config.get(ConfigEnum.APP_SECURITY_OAUTH_RELAX_TOKEN_SCOPE):
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

    # ============================================== SESSION ===========================================================
    session_type = config.get(ConfigEnum.SESSION_TYPE)
    session_prefix = config.get(ConfigEnum.SESSION_KEY_PREFIX)

    log.debug(f'using session type : {session_type}')
    log.debug(f'session prefix : {session_prefix}')

    app.config['SESSION_KEY_PREFIX'] = session_prefix  # 设置session前缀
    session_permanent = config.get(ConfigEnum.SESSION_PERMANENT)
    app.config['SESSION_PERMANENT'] = session_permanent  # session是否永久存活

    if session_permanent:
        # 会话时间永久
        session_permanent_lifetime = config.get(ConfigEnum.SESSION_PERMANENT_LIFETIME)
        app.config['SESSION_PERMANENT_LIFETIME'] = timedelta(seconds=session_permanent_lifetime)
        log.debug(f'enable session permanent, session permanent lifetime: {session_permanent_lifetime}')
    else:
        # 会话将会在浏览器关闭之后清除
        session_lifetime = config.get(ConfigEnum.SESSION_LIFETIME)
        log.debug(f'session lifetime : {session_lifetime}')
        log.debug(f'disable session permanent, session lifetime: {session_lifetime}')

    app.config['SESSION_USE_SIGNER'] = config.get(ConfigEnum.SESSION_USE_SIGNER)  # 会话防止篡改
    app.config['SESSION_COOKIE_SAMESITE'] = config.get(ConfigEnum.SESSION_COOKIE_SAMESITE)  # 会话同源策略
    app.config['SESSION_COOKIE_HTTPONLY'] = config.get(ConfigEnum.SESSION_COOKIE_HTTPONLY)
    app.config['SESSION_COOKIE_SECURE'] = config.get(ConfigEnum.SESSION_COOKIE_SECURE)

    if session_type == 'redis':  # redis存储
        import redis
        app.config['SESSION_TYPE'] = session_type
        host = config.get(ConfigEnum.SESSION_REDIS_HOST)
        port = config.get(ConfigEnum.SESSION_REDIS_PORT)
        database = config.get(ConfigEnum.SESSION_REDIS_DATABASE)
        app.config['SESSION_REDIS'] = redis.StrictRedis(host=host, port=port, db=database)

    elif session_type == 'filesystem':  # filesystem存储
        app.config['SESSION_TYPE'] = session_type

        session_directory = config.get(ConfigEnum.SESSION_FILESYSTEM_FILE_DIRECTORY)
        session_directory_path = path.join(root_path, session_directory)
        log.debug(f'session file directory: {session_directory_path}')

        session_threshold = config.get(ConfigEnum.SESSION_FILESYSTEM_FILE_THRESHOLD)
        app.config['SESSION_FILE_THRESHOLD'] = session_threshold
        app.config['SESSION_FILE_DIR'] = session_directory_path

    session.init_app(app)

    # ============================================== CACHE =============================================================
    cache_type = config.get(ConfigEnum.CACHE_TYPE)
    cache_prefix = config.get(ConfigEnum.CACHE_KEY_PREFIX)

    log.debug(f'using cache type : {session_type}')
    log.debug(f'cache prefix : {cache_prefix}')

    app.config['CACHE_DEFAULT_TIMEOUT'] = config.get(ConfigEnum.CACHE_TIMEOUT)  # 缓存超时时间
    app.config['CACHE_KEY_PREFIX'] = cache_prefix
    app.config['CACHE_IGNORE_ERRORS'] = config.get(ConfigEnum.CACHE_IGNORE_ERRORS)

    if cache_type == 'filesystem':
        # 使用文件系统进行缓存
        cache_directory = config.get(ConfigEnum.CACHE_FILESYSTEM_FILE_DIRECTORY)
        cache_directory_path = path.join(root_path, cache_directory)
        log.debug(f'cache file directory: {cache_directory_path}')

        app.config['CACHE_TYPE'] = cache_type
        app.config['CACHE_DIR'] = cache_directory_path
        app.config['CACHE_THRESHOLD'] = config.get(ConfigEnum.CACHE_FILESYSTEM_FILE_THRESHOLD)

    elif cache_type == 'redis':
        app.config['CACHE_TYPE'] = cache_type
        app.config['CACHE_REDIS_HOST'] = config.get(ConfigEnum.CACHE_REDIS_HOST)
        app.config['CACHE_REDIS_PORT'] = config.get(ConfigEnum.CACHE_REDIS_PORT)
        app.config['CACHE_REDIS_DB'] = config.get(ConfigEnum.CACHE_REDIS_DATABASE)
        app.config['CACHE_REDIS_USERNAME'] = config.get(ConfigEnum.CACHE_REDIS_USERNAME)
        app.config['CACHE_REDIS_PASSWORD'] = config.get(ConfigEnum.CACHE_REDIS_PASSWORD)

    import utils.middlewares
    utils.middlewares.init(app)

    # ============================================== DATABASE ==========================================================
    driver = config.get(ConfigEnum.DATABASE_DRIVER)
    username = config.get(ConfigEnum.DATABASE_USERNAME)
    password = config.get(ConfigEnum.DATABASE_PASSWORD)
    database = config.get(ConfigEnum.DATABASE_DATABASE)
    host = config.get(ConfigEnum.DATABASE_HOST)
    port = config.get(ConfigEnum.DATABASE_PORT)
    track_modification = config.get(ConfigEnum.DATABASE_TRACK_MODIFICATION)

    if driver == 'mysql':
        database_uri = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset=utf8'
    else:
        raise RuntimeError('unsupported driver')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = track_modification  # 追踪模式
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

def init_cors():
    """ 前后端项目需要配置适当跨域 """
    from flask_cors import CORS
    if dev_mode:  # 开发者模式下允许所有跨域
        log.debug(_('enable cors for all router'))
        # 启用CORS对所有路由，并允许携带Access token在Authorization请求头
        CORS(app, resources={r"/api/*": {
            # 如果手动携带Authorization请求头，需要明确来源，而非'*'
            # 因为浏览器可能对'*'来源的响应不作答复
            "origins": "http://localhost:5173",  # todo: 将跨域相关配置迁移到配置文件
            "allow_headers": ["Content-Type", "Accept-Language"],
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"],
        }}, supports_credentials=True)  # 允许cookie session凭证


def init_flasgger():
    """ 初始化项目接口文档(flasgger) """
    if not dev_mode: return  # 仅在开发者模式下开启swagger文档
    from flasgger import Swagger
    swagger_config = {  # swagger初始化
        "title": "Musicatri后端项目API文档",
        "uiversion": 3,
        "description": "Musicatri后端项目API说明文档",
        "version": "0.1.0",
        "termsOfService": "https://blu3evil.github.io/musicatri1",
        "contact": {
            "name": "pineclone",
            "email": "pineclone@outlook.com",
            "url": "https://github.com/eyespore"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    }

    app.config['SWAGGER'] = swagger_config
    Swagger(app)

def init_exception_handler():
    """
    初始化项目异常处理器，用于捕获全局异常来避免在生产环境下异常抛出，在开发者模式下异常处理器会被
    禁止注册，这是为了更好的堆栈轨迹显示，避免在开发阶段无法定位问题
    """
    if dev_mode: return
    @app.errorhandler(404)  # path not found
    def handle_404(exception: Exception) -> Response:
        _ = g.t
        return jsonify({'message': _('not found')})

    @app.errorhandler(500)  # flask error
    def handle_500(exception: Exception) -> Response:
        _ = g.t
        # todo: 此处向开发者提交未知异常消息，记录错误日志信息
        log.debug(str(exception))
        return jsonify({'message': _('internal error')})

    @app.errorhandler(Exception)
    def handle_uncaught(exception: Exception) -> Response:
        _ = g.t
        # todo: 此处向开发者提交未知异常消息，记录错误日志信息
        log.error(_("unknown: %s") % exception)
        return jsonify({'message': _('uncaught error')})

def init_lifecycle():
    """ 初始化flask app生命周期 """
    @app.before_request
    def before_request():
        accept_language = request.headers.get('Accept-Language')  # zh-CN
        g.t = locales.get(accept_language)  # 请求到达前挂载本地化

def run_server():
    """
    初始化socketio，注册项目socketio相关的命名空间，从而支持socketio相关功能
    返回WSGI(Web Server Gateway Interface)，代替原先的flask调试服务作为服务器
    """
    from sockets import socketio
    socketio.init_app(app)

    if dev_mode: log.info(f"using: {socketio.async_mode}")

    host = default_config.get(DefaultConfigTag.SERVER_HOST)  # 服务器主机名
    port = default_config.get(DefaultConfigTag.SERVER_PORT)  # 服务器端口号

    # 同flask一样，使用injector时不建议启用
    log.info(_("musicatri launch successfully"))
    # 开发模式下有wsgi自己的地址绑定回显，不需要额外打印
    if not dev_mode: log.info(_("services listening on: http://%(host)s:%(port)s") % dict(host=host, port=port))

    socketio.run(app=app, host=host, port=port, debug=False, log_output=dev_mode)
    log.info(_("musicatri teardown"))

def init_views():
    """ 蓝图初始化，路由中绝大多数接口使用RESTFUL风格编写 """
    from views.static_blueprint import static_bp
    from views.status_blueprint import status_bp_v1
    from views.auth_blueprint import auth_bp_v1

    app.register_blueprint(static_bp)
    app.register_blueprint(status_bp_v1)
    app.register_blueprint(auth_bp_v1)


def init_database():
    """ 数据库初始化 """
    import domains
    domains.models.init(app)

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

