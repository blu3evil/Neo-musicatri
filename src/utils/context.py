config_schema = {
    # 应用信息配置
    'environment': {'type': 'string', 'default': 'global'},
    'active-environment': {'type': 'string', 'default': 'global'},
    'application': {
        'type': 'dict',
        'schema': {
            'namespace': {'type': 'string', 'default': 'undefined'},
            'dev-mode': {'type': 'boolean', 'default': False},  # 是否开启dev模式
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
        }
    },
}

class DefaultConfigKey:
    # 应用配置
    APP_DEV_MODE = 'application.dev-mode'
    APP_LANGUAGE = 'application.language'
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


import logging
import os, os.path as path

from utils import root_path
from utils.config import Config
from utils.locale import LocaleFactory
from utils.logger import SimpleLoggerFacade

from flask import Flask, session, jsonify, Response
from flask_caching import Cache
from flask_session import Session
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

class ApplicationContextV1:
    """ 服务实例建造器，实现它来快速构建一个服务实例 """
    banner: str  # 旗帜
    namespace: str  # 命名空间
    config_schema: dict  # 配置校验
    using_socketio: bool  # 是否使用socketio

    config: Config  # 配置
    locale: LocaleFactory  # 本地化
    logger: logging.Logger  # 日志

    db: SQLAlchemy  # 数据库
    app: Flask  # 应用
    cache: Cache  # 缓存
    socketio: SocketIO  # 长连接
    session = session  # 会话

    def __init__(self, namespace):
        self.namespace = namespace
        self.config_schema = config_schema
        self.using_socketio = False  # 是否使用socketio

    def pre_init(self):
        """ 预初始化钩子 """
        pass

    def post_init(self):
        """ 初始化后钩子 """
        pass

    def init_config(self):
        """ 初始化配置，配置文件路径位于/config/${namespace}.yaml """
        config_path = path.join(root_path, 'config', f'{self.namespace}.yaml')
        self.config = Config(config_path, self.config_schema)  # 项目配置
        self.config.load()  # 加载配置

    def init_locale(self):
        """ 初始化本地化 """
        locale_dir = path.join(root_path, 'resources', self.namespace, 'locales')
        default_language = self.config.get(DefaultConfigKey.APP_LANGUAGE)  # 默认语言
        self.locale = LocaleFactory(self.namespace, locale_dir, default_language)  # 本地化实例

    def init_logger(self):
        """ 初始化日志 """
        facade = SimpleLoggerFacade()  # 日志配置
        if self.config.get(DefaultConfigKey.APP_LOG_DEFAULT_LOGGING_ENABLE):  # 是否开启配置
            facade.set_default(self.config.get(DefaultConfigKey.APP_LOG_DEFAULT_LOGGING_LEVEL))

            if self.config.get(DefaultConfigKey.APP_LOG_CONSOLE_LOGGING_ENABLE):  # 控制台日志
                facade.set_console(self.config.get(DefaultConfigKey.APP_LOG_CONSOLE_LOGGING_LEVEL))

            if self.config.get(DefaultConfigKey.APP_LOG_LOGFILE_LOGGING_ENABLE):  # 文件日志
                logs_dir = path.join(
                    root_path, 'temp', self.namespace,
                    self.config.get(DefaultConfigKey.APP_LOG_LOGFILE_LOGGING_FILE_DIRECTORY)
                )  # 日志文件创建目录

                extname = self.namespace
                facade.set_filelog(
                    self.config.get(DefaultConfigKey.APP_LOG_LOGFILE_LOGGING_LEVEL),
                    logs_dir,
                    extname
                )  # 日志文件创建位置

        else:
            logging.disable()  # 禁用日志输出
        self.logger = facade.get_logger()  # 默认日志

    def init_flask_app(self):
        """ 初始化flask app """
        dev_mode = self.config.get(DefaultConfigKey.APP_DEV_MODE)
        _ = self.locale.get()

        if dev_mode: self.logger.warning(
            _("dev mode is enabled, know more about development mode at README.md, this mode is only used for "
              "development and testing, do not enable this mode in production environment"))

        self.app = Flask(self.namespace)  # app实例
        secret_key = self.config.get(DefaultConfigKey.APP_SECURITY_SECRET_KEY)
        self.app.config['SECRET_KEY'] = secret_key  # 应用密钥配置

    def init_oauthlib(self):
        """ 初始化oauth lib """
        if self.config.get(DefaultConfigKey.APP_SECURITY_OAUTH_INSECURE_TRANSPORT):
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # 仅https下的oath

        if self.config.get(DefaultConfigKey.APP_SECURITY_OAUTH_RELAX_TOKEN_SCOPE):
            os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'  # 允许oauth2动态权限调整

    def init_cors(self):
        """ 前后端项目需要配置适当跨域 """
        from flask_cors import CORS
        # 启用CORS对所有路由，并允许携带Access token在Authorization请求头
        origins = self.config.get(DefaultConfigKey.APP_SECURITY_CORS_ALLOW_ORIGINS)
        headers = self.config.get(DefaultConfigKey.APP_SECURITY_CORS_ALLOW_HEADERS)
        methods = self.config.get(DefaultConfigKey.APP_SECURITY_CORS_ALLOW_METHODS)
        supports_credentials = self.config.get(DefaultConfigKey.APP_SECURITY_CORS_SUPPORTS_CREDENTIALS)

        CORS(self.app, resources={
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

    def init_flasgger(self):
        """ 初始化项目接口文档(flasgger) """
        dev_mode = self.config.get(DefaultConfigKey.APP_DEV_MODE)
        if not dev_mode: return  # 仅在开发者模式下开启swagger文档

        # todo: flasgger纳入config配置项
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
        self.app.config['SWAGGER'] = swagger_config
        Swagger(self.app)

    def init_exception_handlers(self):
        """ 初始化项目异常处理器 """
        # 注册异常拦截器，不会覆盖原始异常
        def register_errorhandler(status, error_consumer):
            @self.app.errorhandler(status)
            def handler(e):
                _ = self.locale.get()
                self.logger.error(e)  # 记录日志
                response = error_consumer(e, _)
                response.status_code = status
                return response

        register_errorhandler(400, lambda e, _: jsonify({'message': _('Bad Request')}))
        register_errorhandler(401, lambda e, _: jsonify({'message': _('Unauthorized')}))
        register_errorhandler(403, lambda e, _: jsonify({'message': _('Forbidden')}))
        register_errorhandler(404, lambda e, _: jsonify({'message': _('NotFound')}))
        register_errorhandler(500, lambda e, _: jsonify({'message': _('Internal Server Error')}))

        dev_mode = self.config.get(DefaultConfigKey.APP_DEV_MODE)
        if dev_mode: return  # 开发者模式下并不会注册这一项

        @self.app.errorhandler(Exception)
        def handle_uncaught(e: Exception) -> Response:
            _ = self.locale.get()
            # todo: 此处向开发者提交未知异常消息，记录错误日志信息
            self.logger.error(_("unknown: %s") % e)
            response = jsonify({'message': str(e)})
            response.status_code = 400  # 将异常原因归咎于用户
            return response

    def init_session(self):
        session_type = self.config.get(DefaultConfigKey.SESSION_TYPE)
        session_prefix = self.config.get(DefaultConfigKey.SESSION_KEY_PREFIX)
        session_permanent = self.config.get(DefaultConfigKey.SESSION_PERMANENT)

        # log.debug(f'using session type : {session_type}')
        # log.debug(f'session prefix : {session_prefix}')

        self.app.config['SESSION_KEY_PREFIX'] = session_prefix  # 设置session前缀
        self.app.config['SESSION_PERMANENT'] = session_permanent  # session是否永久存活

        from datetime import timedelta
        if session_permanent:
            # 会话时间永久
            session_permanent_lifetime = self.config.get(DefaultConfigKey.SESSION_PERMANENT_LIFETIME)
            self.app.config['SESSION_PERMANENT_LIFETIME'] = timedelta(seconds=session_permanent_lifetime)
            # log.debug(f'enable session permanent, session permanent lifetime: {session_permanent_lifetime}')
        else:
            # 会话将会在浏览器关闭之后清除
            session_lifetime = self.config.get(DefaultConfigKey.SESSION_LIFETIME)
            self.app.config['SESSION_LIFETIME'] = timedelta(seconds=session_lifetime)

            # log.debug(f'session lifetime : {session_lifetime}')
            # log.debug(f'disable session permanent, session lifetime: {session_lifetime}')

        self.app.config['SESSION_USE_SIGNER'] = self.config.get(DefaultConfigKey.SESSION_USE_SIGNER)  # 会话防止篡改
        self.app.config['SESSION_COOKIE_SAMESITE'] = self.config.get(DefaultConfigKey.SESSION_COOKIE_SAMESITE)  # 会话同源策略
        self.app.config['SESSION_COOKIE_HTTPONLY'] = self.config.get(DefaultConfigKey.SESSION_COOKIE_HTTPONLY)
        self.app.config['SESSION_COOKIE_SECURE'] = self.config.get(DefaultConfigKey.SESSION_COOKIE_SECURE)

        if session_type == 'redis':  # redis存储
            import redis
            self.app.config['SESSION_TYPE'] = session_type
            host = self.config.get(DefaultConfigKey.SESSION_REDIS_HOST)
            port = self.config.get(DefaultConfigKey.SESSION_REDIS_PORT)
            database = self.config.get(DefaultConfigKey.SESSION_REDIS_DATABASE)
            self.app.config['SESSION_REDIS'] = redis.StrictRedis(host=host, port=port, db=database)

        elif session_type == 'filesystem':  # filesystem存储
            self.app.config['SESSION_TYPE'] = session_type

            session_directory = self.config.get(DefaultConfigKey.SESSION_FILESYSTEM_FILE_DIRECTORY)
            session_directory_path = path.join(root_path, 'temp', self.namespace, session_directory)
            # log.debug(f'session file directory: {session_directory_path}')

            session_threshold = self.config.get(DefaultConfigKey.SESSION_FILESYSTEM_FILE_THRESHOLD)
            self.app.config['SESSION_FILE_THRESHOLD'] = session_threshold
            self.app.config['SESSION_FILE_DIR'] = session_directory_path

        Session(self.app)

    def init_cache(self):
        """ 初始化缓存，使用flask_caching """
        self.cache = Cache()
        cache_type = self.config.get(DefaultConfigKey.CACHE_TYPE)
        cache_timeout = self.config.get(DefaultConfigKey.CACHE_TIMEOUT)
        cache_prefix = self.config.get(DefaultConfigKey.CACHE_KEY_PREFIX)
        cache_ignore_errors = self.config.get(DefaultConfigKey.CACHE_IGNORE_ERRORS)

        # log.debug(f'using cache type : {cache_type}')
        # log.debug(f'cache prefix : {cache_prefix}')

        self.app.config['CACHE_DEFAULT_TIMEOUT'] = cache_timeout  # 缓存超时时间
        self.app.config['CACHE_KEY_PREFIX'] = cache_prefix

        # if not cache_ignore_errors:
        #     log.debug('musicatri run while ignoring no cache errors')
        self.app.config['CACHE_IGNORE_ERRORS'] = cache_ignore_errors

        if cache_type == 'filesystem':
            # 使用文件系统进行缓存
            cache_directory = self.config.get(DefaultConfigKey.CACHE_FILESYSTEM_FILE_DIRECTORY)
            cache_directory_path = path.join(root_path, 'temp', self.namespace, cache_directory)
            cache_filesystem_threshold = self.config.get(DefaultConfigKey.CACHE_FILESYSTEM_FILE_THRESHOLD)
            # log.debug(f'cache file directory: {cache_directory_path}')

            self.app.config['CACHE_TYPE'] = cache_type
            self.app.config['CACHE_DIR'] = cache_directory_path
            self.app.config['CACHE_THRESHOLD'] = cache_filesystem_threshold

        elif cache_type == 'redis':
            self.app.config['CACHE_TYPE'] = cache_type
            self.app.config['CACHE_REDIS_HOST'] = self.config.get(DefaultConfigKey.CACHE_REDIS_HOST)
            self.app.config['CACHE_REDIS_PORT'] = self.config.get(DefaultConfigKey.CACHE_REDIS_PORT)
            self.app.config['CACHE_REDIS_DB'] = self.config.get(DefaultConfigKey.CACHE_REDIS_DATABASE)
            self.app.config['CACHE_REDIS_USERNAME'] = self.config.get(DefaultConfigKey.CACHE_REDIS_USERNAME)
            self.app.config['CACHE_REDIS_PASSWORD'] = self.config.get(DefaultConfigKey.CACHE_REDIS_PASSWORD)

        self.cache.init_app(self.app)

    def init_database(self):
        """ 初始化数据库 """
        self.db = SQLAlchemy()
        host = self.config.get(DefaultConfigKey.DATABASE_HOST)
        port = self.config.get(DefaultConfigKey.DATABASE_PORT)
        driver = self.config.get(DefaultConfigKey.DATABASE_DRIVER)
        username = self.config.get(DefaultConfigKey.DATABASE_USERNAME)
        password = self.config.get(DefaultConfigKey.DATABASE_PASSWORD)
        database = self.config.get(DefaultConfigKey.DATABASE_DATABASE)
        track_modification = self.config.get(DefaultConfigKey.DATABASE_TRACK_MODIFICATION)

        if driver == 'mysql':
            database_uri = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset=utf8'
        else:
            raise RuntimeError('unsupported driver')

        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = track_modification  # 追踪模式
        self.app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

        # self.db.init_app(self.app)
        # import api_server.domain.models as models
        # models.init(app)

    def print_banner(self):
        """ 打印旗帜 """
        if self.config.get(DefaultConfigKey.APP_LOG_PRINT_BANNER):
            self.logger.info(self.banner)

    # 初始化socketio
    def init_socketio(self):
        """ 初始化socketio，注册项目socketio相关的命名空间 """
        self.socketio = SocketIO()

        origins = self.config.get(DefaultConfigKey.APP_SECURITY_CORS_ALLOW_ORIGINS)  # 配置跨域
        # log.debug(f'socketio origins: {origins}')
        # 禁用socketio本身的session管理，使RESTFUL_API和SOCKETIO共用session

        self.socketio.init_app(
            self.app,
            cors_allowed_origins=origins,
            async_mode='threading',  # 仅支持threading
            manage_session=False
        )

        self.using_socketio = True  # socketio现已推出

        # from sockets import user_socketio, admin_socketio
        # user_socketio.init(socketio)  # 初始化用户socketio服务器
        # admin_socketio.init(socketio)  # 初始化管理员socketio服务器
        # log.debug(f"socketio using server: {socketio.async_mode} ")

    def run_werkzeug(self):
        host = self.config.get(DefaultConfigKey.APP_WSGI_HOST)  # 服务器主机名
        port = self.config.get(DefaultConfigKey.APP_WSGI_PORT)  # 服务器端口号
        debug_mode = self.config.get(DefaultConfigKey.APP_WSGI_WERKZEUG_DEBUG_MODE)  # 调试模式
        log_output = self.config.get(DefaultConfigKey.APP_WSGI_WERKZEUG_LOG_OUTPUT)  # 是否打印flask日志
        use_reloader = self.config.get(DefaultConfigKey.APP_WSGI_WERKZEUG_USE_RELOADER)  # 使用热重载

        if self.using_socketio:
            # 使用socketio运行服务
            self.socketio.run(
                app=self.app,
                host=host,
                port=port,
                debug=debug_mode,
                log_output=log_output,
                use_reloader=use_reloader,
                allow_unsafe_werkzeug=True)  # 使用werkzeug启动flask
        else:
            # 正常使用flask app
            self.app.run(
                host=host,
                port=port,
                debug=debug_mode,
                use_reloader=use_reloader,
            )  # 使用werkzeug启动flask

    def initialize(self):
        self.pre_init()  # 预初始化
        self.init_config()  # 初始化配置
        self.init_locale()  # 初始化本地化
        self.init_logger()  # 初始化日志
        self.init_flask_app()  # 初始化flask
        self.init_oauthlib()  # 初始化oauthlib
        self.init_cors()  # 初始化cors
        self.init_flasgger()  # 初始化flasgger
        self.init_exception_handlers()  # 初始化异常处理器
        self.init_session()  # 初始化会话
        self.init_cache()  # 初始化缓存
        self.init_database()  # 初始化数据库
        self.print_banner()  # 打印旗帜
        self.post_init()  # 初始化后