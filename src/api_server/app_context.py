from __future__ import annotations
from datetime import timedelta
from os import path

from flask import session
from flask_caching import Cache
from flask_session import Session

import os
from flask import Flask, jsonify, Response
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from utils import root_path, LocaleFactory, Config, SimpleLoggerFacade

dev_mode = False                # dev mode

app = Flask(__name__)           # 应用
session = session               # 会话
cache = Cache()                 # 缓存
socketio = SocketIO()           # 连接
db = SQLAlchemy()

schema = {
    # 应用信息配置
    'environment': {'type': 'string', 'default': 'global'},
    'active-environment': {'type': 'string', 'default': 'global'},
    'application': {
        'type': 'dict',
        'schema': {
            # 是否开启dev模式
            'namespace': {'type': 'string', 'default': 'undefined'},
            'dev-mode': {'type': 'boolean', 'default': False},
            'language': {'type': 'string', 'default': 'en-US'},
            'information': {
                'type': 'dict',
                'schema': {
                    'name': {'type': 'string', 'default': 'musicatri'},
                    'version': {'type': 'string', 'default': '1.0.0'},
                    'description': {'type': 'string', 'default': '高知能バイオニックロボット'},
                }
            },
            # 安全配置
            'security': {
                'type': 'dict',
                'schema': {
                    'secret-key': {'type': 'string', 'default': 'musicatri'},
                    'oauth': {
                        'type': 'dict',
                        'schema': {
                            'insecure-transport': {'type': 'boolean', 'default': False},  # 允许在HTTP下执行oauth
                            'relax-token-scope': {'type': 'boolean', 'default': False},  # 允许动态调整oauth申请权限
                        }
                    },
                    'cors': {
                        'type': 'dict',
                        'schema': {
                            'allow-origins': {'type': 'list', 'default': ['http://localhost:5173']},
                            'allow-headers': {'type': 'list', 'default': ['Content-Type', 'Authorization', 'Accept-Language']},
                            'allow-methods': {'type': 'list', 'default': ['GET', 'POST', 'PUT', 'DELETE', 'TRACE']},
                            'supports-credentials': {'type': 'boolean', 'default': True},
                        }
                    }
                }
            },
            # 日志配置
            'logging': {
                'type': 'dict',
                'schema': {
                    'print-banner': {'type': 'boolean', 'default': True},
                    'default-logging': {
                        'type': 'dict',
                        'schema': {
                            'enable': {'type': 'boolean', 'default': True},
                            'level': {'type': 'string', 'default': 'DEBUG'},
                        }
                    },
                    'console-logging': {
                        'type': 'dict',
                        'schema': {
                            'enable': {'type': 'boolean', 'default': True},
                            'level': {'type': 'string', 'default': 'DEBUG'},
                        }
                    },
                    'logfile-logging': {
                        'type': 'dict',
                        'schema': {
                            'enable': {'type': 'boolean', 'default': False},
                            'level': {'type': 'string', 'default': 'DEBUG'},
                            'extname': {'type': 'string', 'default': ''},
                            'file-directory': {'type': 'string', 'default': 'logs'},  # /temp/logs
                        }
                    },
                }
            },
            'wsgi-server': {
                'type': 'dict',
                'schema': {
                    'host': {'type': 'string', 'default': '127.0.0.1'},
                    'port': {'type': 'integer', 'default': 5000},
                    'werkzeug': {
                        'type': 'dict',
                        'schema': {
                            'debug-mode': {'type': 'boolean', 'default': False},
                            'log-output': {'type': 'boolean', 'default': False},
                            'use-reloader': {'type': 'boolean', 'default': False},
                        }
                    },
                    'gunicorn': {
                        'type': 'dict',
                        'schema': {
                            'workers': {'type': 'integer', 'default': 1},
                            'threads': {'type': 'integer', 'default': 4},
                            'daemon': {'type': 'boolean', 'default': False},
                            'worker-class': {'type': 'string', 'default': 'gthread'},
                            'worker-connections': {'type': 'integer', 'default': 2000},  # 仅对eventlet gevent生效
                            'pidfile': {'type': 'string', 'default': 'gunicorn/gunicorn.pid'},
                            'accesslog': {'type': 'string', 'default': 'gunicorn/gunicorn_access.log'},
                            'errorlog': {'type': 'string', 'default': 'gunicorn/gunicorn_error.log'},
                            'loglevel': {'type': 'string', 'default': 'warning'},
                        }
                    }
                }
            },
            'database': {
                'type': 'dict',
                'schema': {
                    'driver': {'type': 'string', 'default': 'mysql'},
                    'host': {'type': 'string', 'default': '127.0.0.1'},
                    'port': {'type': 'integer', 'default': 3306},
                    'username': {'type': 'string', 'default': 'root'},
                    'password': {'type': 'string', 'default': '1234'},
                    'database': {'type': 'string', 'default': 'musicatri-api'},
                    'track-modification': {'type': 'boolean', 'default': False},
                }
            },
            'session': {
                'type': 'dict',
                'schema': {
                    'type': {'type': 'string', 'default': 'filesystem'},
                    'cookie-samesite': {'type': 'string', 'default': 'None'},
                    'cookie-httponly': {'type': 'boolean', 'default': False},
                    'cookie-secure': {'type': 'boolean', 'default': False},  # 仅允许在https下传输cookie
                    'permanent': {'type': 'boolean', 'default': False},
                    'permanent-lifetime': {'type': 'integer', 'default': 3600},
                    'lifetime': {'type': 'integer', 'default': 1800},
                    'use-signer': {'type': 'boolean', 'default': False},
                    'key-prefix': {'type': 'string', 'default': 'session:'},
                    'redis': {
                        'type': 'dict',
                        'schema': {
                            'host': {'type': 'string', 'default': '127.0.0.1'},
                            'port': {'type': 'integer', 'default': 6379},
                            'username': {'type': 'string', 'default': ''},
                            'password': {'type': 'string', 'default': ''},
                            'database': {'type': 'integer', 'default': 0},
                        },
                    },
                    'filesystem': {
                        'type': 'dict',
                        'schema': {
                            'file-threshold': {'type': 'integer', 'default': 5000},
                            'file-directory': {'type': 'string', 'default': 'session'},  # /temp/session
                        }
                    }
                }
            },
            'cache': {
                'type': 'dict',
                'schema': {
                    'type': {'type': 'string', 'default': 'filesystem'},
                    'timeout': {'type': 'integer', 'default': 60},  # 默认缓存过期时间，刷新缓存间隔
                    'key-prefix': {'type': 'string', 'default': 'cache:'},
                    'ignore-errors': {'type': 'boolean', 'default': False},  # 忽略缓存错误
                    'filesystem': {
                        'type': 'dict',
                        'schema': {
                            'file-threshold': {'type': 'integer', 'default': 5000},
                            'file-directory': {'type': 'string', 'default': 'cache'},  # /temp/cache
                        }
                    },
                    'redis': {
                        'type': 'dict',
                        'schema': {
                            'host': {'type': 'string', 'default': '127.0.0.1'},
                            'port': {'type': 'integer', 'default': 6379},
                            'username': {'type': 'string', 'default': ''},
                            'password': {'type': 'string', 'default': ''},
                            'database': {'type': 'integer', 'default': 0},
                        }
                    }
                }
            },
            'yt-dlp': {
                'type': 'dict',
                'schema': {
                    'name': {'type': 'string', 'default': 'musicatri'},
                }
            }
        }
    },
    'services': {
        'type': 'dict',
        'schema': {
            'discord': {
                'type': 'dict',
                'schema': {
                    'api_server-endpoint': {'type': 'string', 'default': 'https://discord.com/api/v10'},
                    'oauth': {
                        'type': 'dict',
                        'schema': {
                            'client-id': {'type': 'string', 'default': 'client-id'},
                            'client-secret': {'type': 'string', 'default': 'client-secret'},
                            'redirect-uri': {'type': 'string', 'default': "http://localhost:5173/api/v1/auth/discord/authorized"},
                            'scope': {'type': 'string', 'default': 'identify guilds guilds.join'}
                        }
                    }
                }
            },
            'neteasecloudmusic-api_server': {
                'type': 'dict',
                'schema': {
                    'url': {'type': 'string', 'default': 'http://127.0.0.1:3000'},
                }
            },
        }
    },
}

class ConfigKey:
    # 应用配置
    APP_DEV_MODE = 'application.dev-mode'
    APP_NAMESPACE = 'application.namespace'
    APP_DEFAULT_LANGUAGE = 'application.language'
    APP_INFO_NAME = 'application.information.name'
    APP_INFO_VERSION = 'application.information.version'
    APP_INFO_DESCRIPTION = 'application.information.description'

    # 安全配置
    APP_SECURITY_SECRET_KEY = 'application.security.secret-key'
    APP_SECURITY_OAUTH_INSECURE_TRANSPORT = 'application.security.oauth.insecure-transport'
    APP_SECURITY_OAUTH_RELAX_TOKEN_SCOPE = 'application.security.oauth.insecure-transport'
    APP_SECURITY_CORS_ALLOW_ORIGINS = 'application.security.cors.allow-origins'
    APP_SECURITY_CORS_ALLOW_HEADERS = 'application.security.cors.allow-headers'
    APP_SECURITY_CORS_ALLOW_METHODS = 'application.security.cors.allow-methods'
    APP_SECURITY_CORS_SUPPORTS_CREDENTIALS = 'application.security.cors.supports-credentials'

    # 日志配置
    APP_LOG_PRINT_BANNER = 'application.logging.print-banner'
    APP_LOG_DEFAULT_LOGGING_ENABLE = 'application.logging.default-logging.enable'
    APP_LOG_DEFAULT_LOGGING_LEVEL = 'application.logging.default-logging.level'
    APP_LOG_CONSOLE_LOGGING_ENABLE = 'application.logging.console-logging.enable'
    APP_LOG_CONSOLE_LOGGING_LEVEL = 'application.logging.console-logging.level'
    APP_LOG_LOGFILE_LOGGING_ENABLE = 'application.logging.logfile-logging.enable'
    APP_LOG_LOGFILE_LOGGING_LEVEL = 'application.logging.logfile-logging.level'
    APP_LOG_LOGFILE_LOGGING_EXTNAME = 'application.logging.logfile-logging.extname'
    APP_LOG_LOGFILE_LOGGING_FILE_DIRECTORY = 'application.logging.logfile-logging.file-directory'

    # WSGI服务器配置
    APP_WSGI_HOST = 'application.wsgi-server.host'
    APP_WSGI_PORT = 'application.wsgi-server.port'
    APP_WSGI_WERKZEUG_DEBUG_MODE = 'application.wsgi-server.werkzeug.debug-mode'
    APP_WSGI_WERKZEUG_LOG_OUTPUT = 'application.wsgi-server.werkzeug.log-output'
    APP_WSGI_WERKZEUG_USE_RELOADER = 'application.wsgi-server.werkzeug.use-reloader'
    APP_WSGI_GUNICORN_WORKERS = 'application.wsgi-server.gunicorn.workers'
    APP_WSGI_GUNICORN_THREADS = 'application.wsgi-server.gunicorn.threads'
    APP_WSGI_GUNICORN_DAEMON = 'application.wsgi-server.gunicorn.daemon'
    APP_WSGI_GUNICORN_WORKER_CLASS = 'application.wsgi-server.gunicorn.worker-class'
    APP_WSGI_GUNICORN_WORKER_CONNECTIONS = 'application.wsgi-server.gunicorn.worker-connections'
    APP_WSGI_GUNICORN_PIDFILE = 'application.wsgi-server.gunicorn.pidfile'
    APP_WSGI_GUNICORN_ACCESSLOG = 'application.wsgi-server.gunicorn.accesslog'
    APP_WSGI_GUNICORN_ERRORLOG = 'application.wsgi-server.gunicorn.errorlog'
    APP_WSGI_GUNICORN_LOGLEVEL = 'application.wsgi-server.gunicorn.loglevel'

    # 数据库配置
    DATABASE_DRIVER = 'application.database.driver'
    DATABASE_HOST = 'application.database.host'
    DATABASE_PORT = 'application.database.port'
    DATABASE_USERNAME = 'application.database.username'
    DATABASE_PASSWORD = 'application.database.password'
    DATABASE_DATABASE = 'application.database.database'
    DATABASE_TRACK_MODIFICATION = 'application.database.track-modification'

    # 会话配置
    SESSION_TYPE = 'application.session.type'
    SESSION_COOKIE_SAMESITE = 'application.session.cookie-samesite'
    SESSION_COOKIE_HTTPONLY = 'application.session.cookie-httponly'
    SESSION_COOKIE_SECURE = 'application.session.cookie-secure'
    SESSION_PERMANENT = 'application.session.permanent'
    SESSION_PERMANENT_LIFETIME = 'application.session.permanent-lifetime'
    SESSION_LIFETIME = 'application.session.lifetime'
    SESSION_USE_SIGNER = 'application.session.use-signer'
    SESSION_KEY_PREFIX = 'application.session.key-prefix'
    SESSION_REDIS_HOST = 'application.session.redis.host'
    SESSION_REDIS_PORT = 'application.session.redis.port'
    SESSION_REDIS_USERNAME = 'application.session.redis.username'
    SESSION_REDIS_PASSWORD = 'application.session.redis.password'
    SESSION_REDIS_DATABASE = 'application.session.redis.database'
    SESSION_FILESYSTEM_FILE_THRESHOLD = 'application.session.filesystem.file-threshold'
    SESSION_FILESYSTEM_FILE_DIRECTORY = 'application.session.filesystem.file-directory'

    # 缓存配置
    CACHE_TYPE = 'application.cache.type'
    CACHE_TIMEOUT = 'application.cache.timeout'
    CACHE_KEY_PREFIX = 'application.cache.key-prefix'
    CACHE_IGNORE_ERRORS = 'application.cache.ignore-errors'
    CACHE_REDIS_HOST = 'application.cache.redis.host'
    CACHE_REDIS_PORT = 'application.cache.redis.port'
    CACHE_REDIS_USERNAME = 'application.cache.redis.username'
    CACHE_REDIS_PASSWORD = 'application.cache.redis.password'
    CACHE_REDIS_DATABASE = 'application.cache.redis.database'
    CACHE_FILESYSTEM_FILE_THRESHOLD = 'application.cache.filesystem.file-threshold'
    CACHE_FILESYSTEM_FILE_DIRECTORY = 'application.cache.filesystem.file-directory'

    YT_DLP_NAME = 'application.yt-dlp.name'

    # discord配置
    DISCORD_API_ENDPOINT = 'services.discord.api_server-endpoint'
    DISCORD_OAUTH_CLIENT_ID = 'services.discord.oauth.client-id'
    DISCORD_OAUTH_CLIENT_SECRET = 'services.discord.oauth.client-secret'
    DISCORD_OAUTH_SCOPE = 'services.discord.oauth.scope'
    DISCORD_OAUTH_REDIRECT_URI = 'services.discord.oauth.redirect-uri'

    # 网易云音乐api配置
    NETEASECLOUDMUSIC_API_URL = 'services.neteasecloudmusic.url'


config_path = path.join(root_path, 'config', 'api-server.yaml')
config = Config(config_path, schema)  # 项目配置

namespace = config.get(ConfigKey.APP_NAMESPACE)
default_language = config.get(ConfigKey.APP_DEFAULT_LANGUAGE) # 默认语言

locale_resource_directory_path = os.path.join(root_path, 'resources', namespace, 'locales')
locales = LocaleFactory(namespace, locale_resource_directory_path, default_language)


def init_dispatcher():  # 初始化事件分发器
    from sockets.dispatcher import init_dispatcher
    init_dispatcher()

def init_config():  # 配置文件初始化
    global dev_mode
    dev_mode = config.get(ConfigKey.APP_DEV_MODE)
    _ = locales.get()

    if dev_mode: log.warning(
        _("dev mode is enabled, know more about development mode at README.md, this mode is only used for "
        "development and testing, do not enable this mode in production environment"))

    app.config['SECRET_KEY'] = config.get(ConfigKey.APP_SECURITY_SECRET_KEY)
    # ============================================== OAUTH =============================================================
    # oauth2开启https
    if config.get(ConfigKey.APP_SECURITY_OAUTH_INSECURE_TRANSPORT):
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # 允许oauth2动态权限调整
    if config.get(ConfigKey.APP_SECURITY_OAUTH_RELAX_TOKEN_SCOPE):
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

# 初始化socketio
def init_socketio():
    """ 初始化socketio，注册项目socketio相关的命名空间 """
    log.debug(f'initialize socketio...')
    origins = config.get(ConfigKey.APP_SECURITY_CORS_ALLOW_ORIGINS)  # 配置跨域
    log.debug(f'socketio origins: {origins}')

    # 禁用socketio本身的session管理，使RESTFUL_API和SOCKETIO共用session
    socketio.init_app(app,
                      cors_allowed_origins=origins,
                      async_mode='threading',
                      manage_session=False)

    from sockets import user_socketio, admin_socketio
    user_socketio.init(socketio)  # 初始化用户socketio服务器
    admin_socketio.init(socketio)  # 初始化管理员socketio服务器
    log.debug(f"socketio using server: {socketio.async_mode} ")

def init_cors():
    """ 前后端项目需要配置适当跨域 """
    from flask_cors import CORS
    log.debug(f'initialize cores...')
    # 启用CORS对所有路由，并允许携带Access token在Authorization请求头
    origins = config.get(ConfigKey.APP_SECURITY_CORS_ALLOW_ORIGINS)
    headers = config.get(ConfigKey.APP_SECURITY_CORS_ALLOW_HEADERS)
    methods = config.get(ConfigKey.APP_SECURITY_CORS_ALLOW_METHODS)
    supports_credentials = config.get(ConfigKey.APP_SECURITY_CORS_SUPPORTS_CREDENTIALS)

    CORS(app, resources={
        # 支持前端调用后端RESTFUL api_server
        # 如果手动携带Authorization请求头，需要明确来源，而非'*'，浏览器可能对'*'来源的响应不作答复
        r"/api/*": {  # 支持restful api_server
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
    from views.static_blueprint import static_bp_v1
    from views.system_blueprint import status_bp_v1
    from views.auth_blueprint import auth_bp_v1
    from views.user_blueprint import user_bp_v1

    app.register_blueprint(static_bp_v1)
    app.register_blueprint(status_bp_v1)
    app.register_blueprint(auth_bp_v1)
    app.register_blueprint(user_bp_v1)

def print_banner():
    """ 打印musicatri旗帜，好康的旗帜 """
    if config.get(ConfigKey.APP_LOG_PRINT_BANNER):
        log.info("""
    ______  ___                _____                _____         _____ 
    ___   |/  /____  _____________(_)_____________ ___  /____________(_)
    __  /|_/ / _  / / /__  ___/__  / _  ___/_  __ `/_  __/__  ___/__  / 
    _  /  / /  / /_/ / _(__  ) _  /  / /__  / /_/ / / /_  _  /    _  /  
    /_/  /_/   \__,_/  /____/  /_/   \___/  \__,_/  \__/  /_/     /_/   """)

def init_session():
    session_type = config.get(ConfigKey.SESSION_TYPE)
    session_prefix = config.get(ConfigKey.SESSION_KEY_PREFIX)

    log.debug(f'using session type : {session_type}')
    log.debug(f'session prefix : {session_prefix}')

    app.config['SESSION_KEY_PREFIX'] = session_prefix  # 设置session前缀
    session_permanent = config.get(ConfigKey.SESSION_PERMANENT)
    app.config['SESSION_PERMANENT'] = session_permanent  # session是否永久存活

    if session_permanent:
        # 会话时间永久
        session_permanent_lifetime = config.get(ConfigKey.SESSION_PERMANENT_LIFETIME)
        app.config['SESSION_PERMANENT_LIFETIME'] = timedelta(seconds=session_permanent_lifetime)
        log.debug(f'enable session permanent, session permanent lifetime: {session_permanent_lifetime}')
    else:
        # 会话将会在浏览器关闭之后清除
        session_lifetime = config.get(ConfigKey.SESSION_LIFETIME)
        app.config['SESSION_LIFETIME'] = timedelta(seconds=session_lifetime)
        log.debug(f'session lifetime : {session_lifetime}')
        log.debug(f'disable session permanent, session lifetime: {session_lifetime}')

    app.config['SESSION_USE_SIGNER'] = config.get(ConfigKey.SESSION_USE_SIGNER)  # 会话防止篡改
    app.config['SESSION_COOKIE_SAMESITE'] = config.get(ConfigKey.SESSION_COOKIE_SAMESITE)  # 会话同源策略
    app.config['SESSION_COOKIE_HTTPONLY'] = config.get(ConfigKey.SESSION_COOKIE_HTTPONLY)
    app.config['SESSION_COOKIE_SECURE'] = config.get(ConfigKey.SESSION_COOKIE_SECURE)

    if session_type == 'redis':  # redis存储
        import redis
        app.config['SESSION_TYPE'] = session_type
        host = config.get(ConfigKey.SESSION_REDIS_HOST)
        port = config.get(ConfigKey.SESSION_REDIS_PORT)
        database = config.get(ConfigKey.SESSION_REDIS_DATABASE)
        app.config['SESSION_REDIS'] = redis.StrictRedis(host=host, port=port, db=database)

    elif session_type == 'filesystem':  # filesystem存储
        app.config['SESSION_TYPE'] = session_type

        session_directory = config.get(ConfigKey.SESSION_FILESYSTEM_FILE_DIRECTORY)
        session_directory_path = path.join(root_path, 'temp', namespace, session_directory)
        log.debug(f'session file directory: {session_directory_path}')

        session_threshold = config.get(ConfigKey.SESSION_FILESYSTEM_FILE_THRESHOLD)
        app.config['SESSION_FILE_THRESHOLD'] = session_threshold
        app.config['SESSION_FILE_DIR'] = session_directory_path

    Session(app)

def init_cache():
    cache_type = config.get(ConfigKey.CACHE_TYPE)
    cache_prefix = config.get(ConfigKey.CACHE_KEY_PREFIX)
    ignore_errors = config.get(ConfigKey.CACHE_IGNORE_ERRORS)

    log.debug(f'using cache type : {cache_type}')
    log.debug(f'cache prefix : {cache_prefix}')

    app.config['CACHE_DEFAULT_TIMEOUT'] = config.get(ConfigKey.CACHE_TIMEOUT)  # 缓存超时时间
    app.config['CACHE_KEY_PREFIX'] = cache_prefix

    if not ignore_errors:
        log.debug('musicatri run while ignoring no cache errors')
    app.config['CACHE_IGNORE_ERRORS'] = ignore_errors

    if cache_type == 'filesystem':
        # 使用文件系统进行缓存
        cache_directory = config.get(ConfigKey.CACHE_FILESYSTEM_FILE_DIRECTORY)
        cache_directory_path = path.join(root_path, 'temp', namespace, cache_directory)
        log.debug(f'cache file directory: {cache_directory_path}')

        app.config['CACHE_TYPE'] = cache_type
        app.config['CACHE_DIR'] = cache_directory_path
        app.config['CACHE_THRESHOLD'] = config.get(ConfigKey.CACHE_FILESYSTEM_FILE_THRESHOLD)

    elif cache_type == 'redis':
        app.config['CACHE_TYPE'] = cache_type
        app.config['CACHE_REDIS_HOST'] = config.get(ConfigKey.CACHE_REDIS_HOST)
        app.config['CACHE_REDIS_PORT'] = config.get(ConfigKey.CACHE_REDIS_PORT)
        app.config['CACHE_REDIS_DB'] = config.get(ConfigKey.CACHE_REDIS_DATABASE)
        app.config['CACHE_REDIS_USERNAME'] = config.get(ConfigKey.CACHE_REDIS_USERNAME)
        app.config['CACHE_REDIS_PASSWORD'] = config.get(ConfigKey.CACHE_REDIS_PASSWORD)
    cache.init_app(app)


def init_database():
    host = config.get(ConfigKey.DATABASE_HOST)
    port = config.get(ConfigKey.DATABASE_PORT)
    driver = config.get(ConfigKey.DATABASE_DRIVER)
    username = config.get(ConfigKey.DATABASE_USERNAME)
    password = config.get(ConfigKey.DATABASE_PASSWORD)
    database = config.get(ConfigKey.DATABASE_DATABASE)
    track_modification = config.get(ConfigKey.DATABASE_TRACK_MODIFICATION)

    if driver == 'mysql':
        database_uri = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset=utf8'
    else:
        raise RuntimeError('unsupported driver')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = track_modification  # 追踪模式
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

    db.init_app(app)
    import api_server.domain.models as models
    models.init(app)

import logging
facade = SimpleLoggerFacade()  # 日志配置
if config.get(ConfigKey.APP_LOG_DEFAULT_LOGGING_ENABLE):
    facade.set_default(config.get(ConfigKey.APP_LOG_DEFAULT_LOGGING_LEVEL))

    if config.get(ConfigKey.APP_LOG_CONSOLE_LOGGING_ENABLE):  # 控制台日志
        facade.set_console(config.get(ConfigKey.APP_LOG_CONSOLE_LOGGING_LEVEL))

    if config.get(ConfigKey.APP_LOG_LOGFILE_LOGGING_ENABLE):  # 文件日志
        logs_directory_path = os.path.join(root_path, 'temp', namespace, config.get(ConfigKey.APP_LOG_LOGFILE_LOGGING_FILE_DIRECTORY))
        extname = config.get(ConfigKey.APP_LOG_LOGFILE_LOGGING_EXTNAME)
        facade.set_filelog(config.get(ConfigKey.APP_LOG_LOGFILE_LOGGING_LEVEL), logs_directory_path ,extname)

else: logging.disable()  # 禁用日志输出
log = facade.get_logger()  # 默认日志

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
