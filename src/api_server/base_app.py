from __future__ import annotations
from datetime import timedelta
from os import path

from flask import session
from flask_caching import Cache
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

import os
from flask import Flask, jsonify, Response
from flask_socketio import SocketIO
from utils import config, ConfigEnum, log, locales

root_path = path.dirname(path.dirname(path.abspath(__file__)))          # root path

session = session       # 会话
cache = Cache()         # 缓存
db = SQLAlchemy()       # 数据库

dev_mode = False                # dev mode
debug_mode = False              # debug mode
app = Flask(__name__)           # flak app
socketio = SocketIO()           # 长连接

def init_dispatcher():  # 初始化事件分发器
    from sockets.dispatcher import init_dispatcher
    init_dispatcher()

def init_config():  # 配置文件初始化
    global dev_mode
    global debug_mode
    dev_mode = config.get(ConfigEnum.APP_DEV_MODE)
    _ = locales.get()

    if dev_mode: log.warning(
        _("dev mode is enabled, know more about development mode at README.md, this mode is only used for "
        "development and testing, do not enable this mode in production environment"))

    app.config['SECRET_KEY'] = config.get(ConfigEnum.APP_SECURITY_SECRET_KEY)
    # ============================================== OAUTH =============================================================
    # oauth2开启https
    if config.get(ConfigEnum.APP_SECURITY_OAUTH_INSECURE_TRANSPORT):
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # 允许oauth2动态权限调整
    if config.get(ConfigEnum.APP_SECURITY_OAUTH_RELAX_TOKEN_SCOPE):
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

# 初始化socketio
def init_socketio():
    """ 初始化socketio，注册项目socketio相关的命名空间 """
    log.debug(f'initialize socketio...')
    origins = config.get(ConfigEnum.APP_SECURITY_CORS_ALLOW_ORIGINS)  # 配置跨域
    log.debug(f'socketio origins: {origins}')

    # 禁用socketio本身的session管理，使RESTFUL_API和SOCKETIO共用session
    socketio.init_app(app,
                      cors_allowed_origins=origins,
                      async_mode='threading',
                      manage_session=False)

    from sockets import user_socketio, admin_socketio
    user_socketio.init(socketio)  # 初始化用户socketio服务器
    admin_socketio.init(socketio)  # 初始化管理员socketio服务器
    log.debug(f"socketio using server: {socketio.async_mode}")


def init_cors():
    """ 前后端项目需要配置适当跨域 """
    from flask_cors import CORS
    log.debug(f'initialize cores...')
    # 启用CORS对所有路由，并允许携带Access token在Authorization请求头
    origins = config.get(ConfigEnum.APP_SECURITY_CORS_ALLOW_ORIGINS)
    headers = config.get(ConfigEnum.APP_SECURITY_CORS_ALLOW_HEADERS)
    methods = config.get(ConfigEnum.APP_SECURITY_CORS_ALLOW_METHODS)
    supports_credentials = config.get(ConfigEnum.APP_SECURITY_CORS_SUPPORTS_CREDENTIALS)

    CORS(app, resources={
        # 支持前端调用后端RESTFUL api_server
        # 如果手动携带Authorization请求头，需要明确来源，而非'*'，浏览器可能对'*'来源的响应不作答复
        r"/api_server/*": {  # 支持restful api_server
            "origins": origins,
            "allow_headers": headers,
            "allow_methods": methods,
        },
        r"/socket.io/*": {  # 支持socketio
            "origins": origins,
            "allow_headers": headers,
            "allow_methods": methods,
        }
    }, supports_credentials=supports_credentials)  # 允许cookie session凭证


def init_flasgger():
    """ 初始化项目接口文档(flasgger) """
    if not dev_mode: return  # 仅在开发者模式下开启swagger文档
    log.debug(f'initialize flasgger...')
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


def init_exception_handlers():
    """ 初始化项目异常处理器 """
    log.debug(f'initialize error handlers...')
    # 注册异常拦截器，不会覆盖原始异常
    def register_errorhandler(status, error_consumer):
        @app.errorhandler(status)
        def handler(e):
            _ = locales.get()
            log.error(e)  # 记录日志
            response = error_consumer(e, _)
            response.status_code = status
            return response

    register_errorhandler(400, lambda e, _: jsonify({'message': _('Bad Request')}))
    register_errorhandler(401, lambda e, _: jsonify({'message': _('Unauthorized')}))
    register_errorhandler(403, lambda e, _: jsonify({'message': _('Forbidden')}))
    register_errorhandler(404, lambda e, _: jsonify({'message': _('NotFound')}))
    register_errorhandler(500, lambda e, _: jsonify({'message': _('Internal Server Error')}))

    if dev_mode: return  # 开发者模式下并不会注册这一项
    @app.errorhandler(Exception)
    def handle_uncaught(e: Exception) -> Response:
        _ = locales.get()
        # todo: 此处向开发者提交未知异常消息，记录错误日志信息
        log.error(_("unknown: %s") % e)
        response = jsonify({'message': str(e)})
        response.status_code = 400  # 将异常原因归咎于用户
        return response


def init_app_event():
    """ 初始化flask app生命周期 """
    log.debug(f'initialize event binding...')

def init_views():
    log.debug(f'initialize views...')
    """ 蓝图初始化 """
    from views.static_blueprint import static_bp
    from views.system_blueprint import status_bp_v1
    from views.auth_blueprint import auth_bp_v1
    from views.user_blueprint import user_bp_v1
    # from views.atri_blueprint import atri_bp_v1

    app.register_blueprint(static_bp)
    app.register_blueprint(status_bp_v1)
    app.register_blueprint(auth_bp_v1)
    app.register_blueprint(user_bp_v1)
    # app.register_blueprint(atri_bp_v1)

def print_banner():
    """ 打印musicatri旗帜，好康的旗帜 """
    if config.get(ConfigEnum.APP_LOG_PRINT_BANNER):
        log.info("""
    ______  ___                _____                _____         _____ 
    ___   |/  /____  _____________(_)_____________ ___  /____________(_)
    __  /|_/ / _  / / /__  ___/__  / _  ___/_  __ `/_  __/__  ___/__  / 
    _  /  / /  / /_/ / _(__  ) _  /  / /__  / /_/ / / /_  _  /    _  /  
    /_/  /_/   \__,_/  /____/  /_/   \___/  \__,_/  \__/  /_/     /_/   """)

def init_session():
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
        app.config['SESSION_LIFETIME'] = timedelta(seconds=session_lifetime)
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
        session_directory_path = path.join(root_path, 'tmp', session_directory)
        log.debug(f'session file directory: {session_directory_path}')

        session_threshold = config.get(ConfigEnum.SESSION_FILESYSTEM_FILE_THRESHOLD)
        app.config['SESSION_FILE_THRESHOLD'] = session_threshold
        app.config['SESSION_FILE_DIR'] = session_directory_path

    Session(app)

def init_cache():
    cache_type = config.get(ConfigEnum.CACHE_TYPE)
    cache_prefix = config.get(ConfigEnum.CACHE_KEY_PREFIX)
    ignore_errors = config.get(ConfigEnum.CACHE_IGNORE_ERRORS)

    log.debug(f'using cache type : {cache_type}')
    log.debug(f'cache prefix : {cache_prefix}')

    app.config['CACHE_DEFAULT_TIMEOUT'] = config.get(ConfigEnum.CACHE_TIMEOUT)  # 缓存超时时间
    app.config['CACHE_KEY_PREFIX'] = cache_prefix

    if not ignore_errors:
        log.debug('musicatri run while ignoring no cache errors')
    app.config['CACHE_IGNORE_ERRORS'] = ignore_errors

    if cache_type == 'filesystem':
        # 使用文件系统进行缓存
        cache_directory = config.get(ConfigEnum.CACHE_FILESYSTEM_FILE_DIRECTORY)
        cache_directory_path = path.join(root_path, 'tmp', cache_directory)
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

    cache.init_app(app)


def init_database():
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

    from dao.models import init
    init(app)  # 初始化库表

def setup_app():
    init_config()  # 配置文件初始化
    init_exception_handlers()  # 初始化异常处理器
    init_cors()  # 初始化cores
    init_app_event()  # 初始化生命事件钩子
    init_session()  # 初始化session
    init_cache()  # 初始化caching
    init_database()  # 初始化database
    init_socketio()  # 初始化socketio
    init_dispatcher()  # 初始化事件分发器
    init_views()  # 初始化蓝图
    init_flasgger()  # 初始化接口文档
    print_banner()  # 打印旗帜
