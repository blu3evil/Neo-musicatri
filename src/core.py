from datetime import timedelta
from os import path

from flask import Flask, session
from flask_caching import Cache
from flask_session import Session
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from utils import config, ConfigEnum, log

root_path = path.dirname(path.dirname(path.abspath(__file__)))          # root path

session = session       # 会话
cache = Cache()         # 缓存
db = SQLAlchemy()       # 数据库
socketio = SocketIO()   # 长连接

def init(app: Flask):
    init_session(app)
    init_cache(app)
    init_database(app)
    init_socketio(app)

# 初始化socketio
def init_socketio(app: Flask):
    """ 初始化socketio，注册项目socketio相关的命名空间 """
    log.debug(f'initialize socketio...')
    origins = config.get(ConfigEnum.APP_NETWORK_CORS_ALLOW_ORIGINS)  # 配置跨域
    log.debug(f'socketio origins: {origins}')
    socketio.init_app(app, cors_allowed_origins=origins)

    from sockets import user_socketio
    user_socketio.init(socketio)
    log.debug(f"socketio using server: {socketio.async_mode}")


def init_session(app: Flask):
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

    Session(app)


def init_cache(app: Flask):
    cache_type = config.get(ConfigEnum.CACHE_TYPE)
    cache_prefix = config.get(ConfigEnum.CACHE_KEY_PREFIX)

    log.debug(f'using cache type : {cache_type}')
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

    cache.init_app(app)


def init_database(app: Flask):
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

    db.init_app(app)
    from dao.models import init
    # 初始化库表
    init(app)