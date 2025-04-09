from __future__ import annotations

config_schema = {
    # 应用信息配置
    'environment': {'type': 'string', 'default': 'global'},
    'active-environment': {'type': 'string', 'default': 'global'},
    'application': {
        'type': 'dict',
        'schema': {
            'namespace': {'type': 'string', 'default': 'undefined'},
            'dev-mode': {'type': 'boolean', 'default': False},  # 是否开启dev模式
            'language': {'type': 'string', 'default': 'en-US'},  # 首选语言
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
            }
        }
    }
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

import logging
import os, os.path as path

from utils import root_path
from utils.config import Config
from utils.locale import LocaleFactory
from utils.logger import SimpleLoggerFacade

from flask import Flask, jsonify, Response
from flask_caching import Cache
from flask_session import Session
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy


class GunicornConfig:
    """ gunicorn上下文，包含gunicorn配置项 """
    workers: int  # 进程数
    threads: int  # 线程数
    bind: str  # 端口ip
    daemon: bool  # 是否后台运行
    worker_class: str  # 工作模式协程，例如gthread, eventlet
    worker_connections: int  # 最大连接数（并发量）
    pidfile: str  # gunicorn进程文件'/var/run/gunicorn.pid'
    accesslog: str  # 设置访问日志和错误信息日志路径'/var/log/gunicorn_access.log'
    errorlog: str  # '/var/log/gunicorn_error.log'
    loglevel: str  # 设置日志记录水平 warning

from typing import Callable
from collections import OrderedDict
class ApplicationContextV1:
    """ 服务实例建造器，实现它来快速构建一个服务实例 """
    banner: str  # 旗帜
    namespace: str  # 命名空间
    config_schema: dict  # 配置校验
    priority_plugin_setups: OrderedDict  # 优先级插件初始化

    config: Config  # 配置
    locale: LocaleFactory  # 本地化
    logger: logging.Logger  # 日志

    app: Flask  # 应用

    def __init__(self, namespace):
        self.namespace = namespace
        self.config_schema = config_schema
        self.priority_plugin_setups = OrderedDict()

    def modify_config_schema(self, schema: dict):
        """ 修改配置结构，用于添加 """

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

    def init_locale(self):
        """ 初始化本地化 """
        locale_dir = path.join(root_path, 'resources', self.namespace, 'locales')
        default_language = self.config.get(DefaultConfigKey.APP_LANGUAGE)  # 默认语言
        self.locale = LocaleFactory(self.namespace, locale_dir, default_language)  # 本地化实例

    def init_flask_app(self):
        """ 初始化flask app """
        dev_mode = self.config.get(DefaultConfigKey.APP_DEV_MODE)
        _ = self.locale.get()
        if dev_mode: self.logger.warning(_(
            "dev mode is enabled, know more about development mode at README.md, this mode is only used for "
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

    def print_banner(self):
        """ 打印旗帜 """
        if self.config.get(DefaultConfigKey.APP_LOG_PRINT_BANNER):
            self.logger.info(self.banner)

    def run_werkzeug(self):
        """ 使用werkzeug启动flask """
        host = self.config.get(DefaultConfigKey.APP_WSGI_HOST)  # 服务器主机名
        port = self.config.get(DefaultConfigKey.APP_WSGI_PORT)  # 服务器端口号
        debug_mode = self.config.get(DefaultConfigKey.APP_WSGI_WERKZEUG_DEBUG_MODE)  # 调试模式
        log_output = self.config.get(DefaultConfigKey.APP_WSGI_WERKZEUG_LOG_OUTPUT)  # 是否打印flask日志
        use_reloader = self.config.get(DefaultConfigKey.APP_WSGI_WERKZEUG_USE_RELOADER)  # 使用热重载

        self.app.run(
            host=host,
            port=port,
            debug=debug_mode,
            use_reloader=use_reloader,
        )

    @property
    def gunicorn_config(self) -> GunicornConfig:
        config = GunicornConfig()
        """ gunicorn上下文，包含gunicorn配置项 """
        config.workers = self.config.get(DefaultConfigKey.APP_WSGI_GUNICORN_WORKERS)  # 进程数
        config.threads = self.config.get(DefaultConfigKey.APP_WSGI_GUNICORN_THREADS)  # 线程数
        config.bind = f'{self.config.get(DefaultConfigKey.APP_WSGI_HOST)}:{self.config.get(DefaultConfigKey.APP_WSGI_PORT)}'  # 端口ip
        config.daemon = self.config.get(DefaultConfigKey.APP_WSGI_GUNICORN_DAEMON)  # 是否后台运行
        config.worker_class = self.config.get(DefaultConfigKey.APP_WSGI_GUNICORN_WORKER_CLASS)  # 工作模式协程
        config.worker_connections = self.config.get(DefaultConfigKey.APP_WSGI_GUNICORN_WORKER_CONNECTIONS)  # 最大连接数（并发量）

        # todo: 修复gunicorn启动时的pidfile accesslog errorlog配置问题
        config.pidfile = path.join(root_path, 'temp', self.namespace, self.config.get(DefaultConfigKey.APP_WSGI_GUNICORN_PIDFILE))  # gunicorn进程文件'/var/run/gunicorn.pid'
        config.accesslog = path.join(root_path, 'temp', self.namespace, self.config.get(DefaultConfigKey.APP_WSGI_GUNICORN_ACCESSLOG))  # 设置访问日志和错误信息日志路径'/var/log/gunicorn_access.log'
        config.errorlog = path.join(root_path, 'temp', self.namespace, self.config.get(DefaultConfigKey.APP_WSGI_GUNICORN_ERRORLOG))  # '/var/log/gunicorn_error.log'
        config.loglevel = self.config.get(DefaultConfigKey.APP_WSGI_GUNICORN_LOGLEVEL)  # 设置日志记录水平 warning
        return config

    def append_priority_plugin_setup(self, plugin_setup: Callable[[ApplicationContextV1], None], priority: int=-1) -> None:
        if priority not in self.priority_plugin_setups:
            self.priority_plugin_setups[priority] = []
        self.priority_plugin_setups[priority].append(plugin_setup)

    def init_priority_plugins(self):
        for priority in sorted(self.priority_plugin_setups.keys(), reverse=True):  # 降序执行初始化闭包
            for priority_plugin_setup in self.priority_plugin_setups[priority]:
                priority_plugin_setup(self)

    def initialize(self):
        self.modify_config_schema(self.config_schema)  # 加载自定义配置
        self.pre_init()  # 预初始化
        self.init_config()  # 初始化配置
        self.init_logger()  # 初始化日志
        self.init_locale()  # 初始化本地化
        self.init_flask_app()  # 初始化flask
        self.init_oauthlib()  # 初始化oauthlib
        self.init_exception_handlers()  # 初始化异常处理器
        self.print_banner()  # 打印旗帜
        self.init_priority_plugins()  # 初始化优先级插件
        self.post_init()  # 初始化后

from typing import Type, TypeVar
T = TypeVar('T', bound=ApplicationContextV1)


class ApplicationContextPlugin:
    """ 上下文插件父类，通过继承上下文插件类来实现为服务上下文编写拓展插件 """
    priority = -1  # 优先级，初始化闭包执行顺序依据
    def modify_config_schema(self, schema: dict):
        """ 拓展配置结构 """
        pass

    def plugin_setup(self, ctx: T):
        """ 插件初始化 """
        pass

    def __call__(self, ctx: Type[T]):
        plugin_self = self
        class EnhancedApplicationContext(ctx):
            def __init__(self):
                super(EnhancedApplicationContext, self).__init__()
                plugin_self.modify_config_schema(self.config_schema)  # 拓展配置结构
                self.append_priority_plugin_setup(plugin_self.plugin_setup, priority=plugin_self.priority)
        return EnhancedApplicationContext


class CorsConfigKey:
    SECURITY_CORS_ALLOW_ORIGINS = 'application.security.cors.allow-origins'
    SECURITY_CORS_ALLOW_HEADERS = 'application.security.cors.allow-headers'
    SECURITY_CORS_ALLOW_METHODS = 'application.security.cors.allow-methods'
    SECURITY_CORS_SUPPORTS_CREDENTIALS = 'application.security.cors.supports-credentials'

class EnableCors(ApplicationContextPlugin):
    priority = 1  # socketio依赖cors配置项
    """ 启用cors """
    def modify_config_schema(self, schema: dict):
        schema['application']['schema']['security']['schema']['cors'] = {
            'type': 'dict',
            'schema': {
                'allow-origins': {'type': 'list', 'default': ['http://localhost:5173']},
                'allow-headers': {'type': 'list', 'default': ['Content-Type', 'Authorization', 'Accept-Language']},
                'allow-methods': {'type': 'list', 'default': ['GET', 'POST', 'PUT', 'DELETE', 'TRACE']},
                'supports-credentials': {'type': 'boolean', 'default': True},
            }
        }

    def plugin_setup(self, ctx: T):
        """ 前后端项目需要配置适当跨域 """
        from flask_cors import CORS
        # 启用CORS对所有路由，并允许携带Access token在Authorization请求头
        origins = ctx.config.get(CorsConfigKey.SECURITY_CORS_ALLOW_ORIGINS)
        headers = ctx.config.get(CorsConfigKey.SECURITY_CORS_ALLOW_HEADERS)
        methods = ctx.config.get(CorsConfigKey.SECURITY_CORS_ALLOW_METHODS)
        supports_credentials = ctx.config.get(CorsConfigKey.SECURITY_CORS_SUPPORTS_CREDENTIALS)

        CORS(ctx.app, resources={
            # 支持前端调用后端RESTFUL auth_server
            # 如果手动携带Authorization请求头，需要明确来源，而非'*'，浏览器可能对'*'来源的响应不作答复
            r"/api/*": {  # 支持restful auth_server
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

class SessionConfigKey:
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


class SessionEnhance(ApplicationContextPlugin):
    """ 会话增强 """
    def modify_config_schema(self, schema: dict):
        schema['application']['schema']['session'] = {
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
        }

    def plugin_setup(self, ctx: T):
        from flask import session as flask_session
        ctx.session = flask_session

        session_type = ctx.config.get(SessionConfigKey.SESSION_TYPE)
        session_prefix = ctx.config.get(SessionConfigKey.SESSION_KEY_PREFIX)
        session_permanent = ctx.config.get(SessionConfigKey.SESSION_PERMANENT)

        # log.debug(f'using session type : {session_type}')
        # log.debug(f'session prefix : {session_prefix}')

        ctx.app.config['SESSION_KEY_PREFIX'] = session_prefix  # 设置session前缀
        ctx.app.config['SESSION_PERMANENT'] = session_permanent  # session是否永久存活

        from datetime import timedelta
        if session_permanent:
            # 会话时间永久
            session_permanent_lifetime = ctx.config.get(SessionConfigKey.SESSION_PERMANENT_LIFETIME)
            ctx.app.config['SESSION_PERMANENT_LIFETIME'] = timedelta(seconds=session_permanent_lifetime)
            # log.debug(f'enable session permanent, session permanent lifetime: {session_permanent_lifetime}')
        else:
            # 会话将会在浏览器关闭之后清除
            session_lifetime = ctx.config.get(SessionConfigKey.SESSION_LIFETIME)
            ctx.app.config['SESSION_LIFETIME'] = timedelta(seconds=session_lifetime)

            # log.debug(f'session lifetime : {session_lifetime}')
            # log.debug(f'disable session permanent, session lifetime: {session_lifetime}')

        ctx.app.config['SESSION_USE_SIGNER'] = ctx.config.get(SessionConfigKey.SESSION_USE_SIGNER)  # 会话防止篡改
        ctx.app.config['SESSION_COOKIE_SAMESITE'] = ctx.config.get(SessionConfigKey.SESSION_COOKIE_SAMESITE)  # 会话同源策略
        ctx.app.config['SESSION_COOKIE_HTTPONLY'] = ctx.config.get(SessionConfigKey.SESSION_COOKIE_HTTPONLY)
        ctx.app.config['SESSION_COOKIE_SECURE'] = ctx.config.get(SessionConfigKey.SESSION_COOKIE_SECURE)

        if session_type == 'redis':  # redis存储
            import redis
            ctx.app.config['SESSION_TYPE'] = session_type
            host = ctx.config.get(SessionConfigKey.SESSION_REDIS_HOST)
            port = ctx.config.get(SessionConfigKey.SESSION_REDIS_PORT)
            database = ctx.config.get(SessionConfigKey.SESSION_REDIS_DATABASE)
            ctx.app.config['SESSION_REDIS'] = redis.StrictRedis(host=host, port=port, db=database)

        elif session_type == 'filesystem':  # filesystem存储
            ctx.app.config['SESSION_TYPE'] = session_type

            session_directory = ctx.config.get(SessionConfigKey.SESSION_FILESYSTEM_FILE_DIRECTORY)
            session_directory_path = path.join(root_path, 'temp', ctx.namespace, session_directory)
            # log.debug(f'session file directory: {session_directory_path}')

            session_threshold = ctx.config.get(SessionConfigKey.SESSION_FILESYSTEM_FILE_THRESHOLD)
            ctx.app.config['SESSION_FILE_THRESHOLD'] = session_threshold
            ctx.app.config['SESSION_FILE_DIR'] = session_directory_path

        Session(ctx.app)

class CacheConfigKey:
    """ 缓存配置 """
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


class EnableCache(ApplicationContextPlugin):
    """ 启用缓存 """
    priority = -1
    def modify_config_schema(self, schema: dict):
        schema['application']['schema']['cache'] = {
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
        }

    def plugin_setup(self, ctx: T):
        """ 初始化缓存，使用flask_caching """
        ctx.cache = Cache()
        cache_type = ctx.config.get(CacheConfigKey.CACHE_TYPE)
        cache_timeout = ctx.config.get(CacheConfigKey.CACHE_TIMEOUT)
        cache_prefix = ctx.config.get(CacheConfigKey.CACHE_KEY_PREFIX)
        cache_ignore_errors = ctx.config.get(CacheConfigKey.CACHE_IGNORE_ERRORS)

        # log.debug(f'using cache type : {cache_type}')
        # log.debug(f'cache prefix : {cache_prefix}')

        ctx.app.config['CACHE_DEFAULT_TIMEOUT'] = cache_timeout  # 缓存超时时间
        ctx.app.config['CACHE_KEY_PREFIX'] = cache_prefix

        # if not cache_ignore_errors:
        #     log.debug('musicatri run while ignoring no cache errors')
        ctx.app.config['CACHE_IGNORE_ERRORS'] = cache_ignore_errors

        if cache_type == 'filesystem':
            # 使用文件系统进行缓存
            cache_directory = ctx.config.get(CacheConfigKey.CACHE_FILESYSTEM_FILE_DIRECTORY)
            cache_directory_path = path.join(root_path, 'temp', ctx.namespace, cache_directory)
            cache_filesystem_threshold = ctx.config.get(CacheConfigKey.CACHE_FILESYSTEM_FILE_THRESHOLD)
            # log.debug(f'cache file directory: {cache_directory_path}')

            ctx.app.config['CACHE_TYPE'] = cache_type
            ctx.app.config['CACHE_DIR'] = cache_directory_path
            ctx.app.config['CACHE_THRESHOLD'] = cache_filesystem_threshold

        elif cache_type == 'redis':
            ctx.app.config['CACHE_TYPE'] = cache_type
            ctx.app.config['CACHE_REDIS_HOST'] = ctx.config.get(CacheConfigKey.CACHE_REDIS_HOST)
            ctx.app.config['CACHE_REDIS_PORT'] = ctx.config.get(CacheConfigKey.CACHE_REDIS_PORT)
            ctx.app.config['CACHE_REDIS_DB'] = ctx.config.get(CacheConfigKey.CACHE_REDIS_DATABASE)
            ctx.app.config['CACHE_REDIS_USERNAME'] = ctx.config.get(CacheConfigKey.CACHE_REDIS_USERNAME)
            ctx.app.config['CACHE_REDIS_PASSWORD'] = ctx.config.get(CacheConfigKey.CACHE_REDIS_PASSWORD)

        ctx.cache.init_app(ctx.app)


class DatabaseConfigKey:
    # 数据库配置
    DATABASE_DRIVER = 'application.database.driver'
    DATABASE_HOST = 'application.database.host'
    DATABASE_PORT = 'application.database.port'
    DATABASE_USERNAME = 'application.database.username'
    DATABASE_PASSWORD = 'application.database.password'
    DATABASE_DATABASE = 'application.database.database'
    DATABASE_TRACK_MODIFICATION = 'application.database.track-modification'

class EnableDatabase(ApplicationContextPlugin):
    """ 启用数据库 """
    priority = -1

    def modify_config_schema(self, schema: dict):
        schema['application']['schema']['database'] = {
            'type': 'dict',
            'schema': {
                'driver': {'type': 'string', 'default': 'mysql'},
                'host': {'type': 'string', 'default': '127.0.0.1'},
                'port': {'type': 'integer', 'default': 3306},
                'username': {'type': 'string', 'default': 'root'},
                'password': {'type': 'string', 'default': '1234'},
                'database': {'type': 'string', 'default': 'musicatri-database'},
                'track-modification': {'type': 'boolean', 'default': False},
            }
        }

    def plugin_setup(self, ctx: T):
        """ 初始化数据库 """
        ctx.db = SQLAlchemy()
        host = ctx.config.get(DatabaseConfigKey.DATABASE_HOST)
        port = ctx.config.get(DatabaseConfigKey.DATABASE_PORT)
        driver = ctx.config.get(DatabaseConfigKey.DATABASE_DRIVER)
        username = ctx.config.get(DatabaseConfigKey.DATABASE_USERNAME)
        password = ctx.config.get(DatabaseConfigKey.DATABASE_PASSWORD)
        database = ctx.config.get(DatabaseConfigKey.DATABASE_DATABASE)
        track_modification = ctx.config.get(DatabaseConfigKey.DATABASE_TRACK_MODIFICATION)

        if driver == 'mysql':
            database_uri = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset=utf8'
        else:
            raise RuntimeError('unsupported driver')

        ctx.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = track_modification  # 追踪模式
        ctx.app.config['SQLALCHEMY_DATABASE_URI'] = database_uri


class SocketIOConfigKey:
    SOCKETIO_CORS_ALLOW_ORIGINS = 'application.socketio.cors.allow-origins'

class EnableSocketIO(ApplicationContextPlugin):
    """ 开启socketio """
    priority = -1
    def __call__(self, ctx: Type[T]):
        plugin_self = self
        class EnhancedApplicationContext(ctx):
            def __init__(self):
                super(EnhancedApplicationContext, self).__init__()
                plugin_self.modify_config_schema(self.config_schema)  # 拓展配置结构
                self.append_priority_plugin_setup(plugin_self.plugin_setup, priority=plugin_self.priority)

            def run_werkzeug(self):
                """ 覆写run_werkzeug启动流程 """
                # 覆写原始的run_werkzeug启动流程，在socketio启动时需要通过socketio实例直接启动flask
                host = self.config.get(DefaultConfigKey.APP_WSGI_HOST)  # 服务器主机名
                port = self.config.get(DefaultConfigKey.APP_WSGI_PORT)  # 服务器端口号
                debug_mode = self.config.get(DefaultConfigKey.APP_WSGI_WERKZEUG_DEBUG_MODE)  # 调试模式
                log_output = self.config.get(DefaultConfigKey.APP_WSGI_WERKZEUG_LOG_OUTPUT)  # 是否打印flask日志
                use_reloader = self.config.get(DefaultConfigKey.APP_WSGI_WERKZEUG_USE_RELOADER)  # 使用热重载

                self.socketio.run(
                    app=self.app,
                    host=host,
                    port=port,
                    debug=debug_mode,
                    log_output=log_output,
                    use_reloader=use_reloader,
                    allow_unsafe_werkzeug=True
                )  # 使用werkzeug启动flask
        return EnhancedApplicationContext

    def modify_config_schema(self, schema: dict):
        schema['application']['schema']['socketio'] = {
            'type': 'dict',
            'schema': {
                'cors': {
                    'type': 'dict',
                    'schema': {
                        'allow-origins': {'type': 'list', 'default': ['http://localhost:5173']},
                    }
                }
            }
        }

    def plugin_setup(self, ctx: T):
        """ 初始化socketio插件 """
        origins = ctx.config.get(SocketIOConfigKey.SOCKETIO_CORS_ALLOW_ORIGINS)  # 配置跨域
        # 禁用socketio本身的session管理，使RESTFUL_API和SOCKETIO共用session
        ctx.socketio = SocketIO()  # 创建socketio实例
        ctx.socketio.init_app(
            ctx.app,
            cors_allowed_origins=origins,
            async_mode='threading',  # todo: 修改支持其他服务启动形式
            manage_session=False
        )

        # from sockets import user_socketio, admin_socketio
        # user_socketio.init(socketio)  # 初始化用户socketio服务器
        # admin_socketio.init(socketio)  # 初始化管理员socketio服务器
        # log.debug(f"socketio using server: {socketio.async_mode} ")

        ctx.logger.info(f'socketio enabled for application context [{ctx.namespace}]')


class NacosConfigKey:
    NACOS_SERVER_ADDR = 'application.nacos.server-addr'  # nacos服务端地址
    NACOS_SERVER_PORT = 'application.nacos.server-port'  # nacos服务端地址
    NACOS_REG_SERVICE_NAME = 'application.nacos.registration.service-name'  # 服务名称
    NACOS_REG_SERVICE_ADDR = 'application.nacos.registration.service-addr'  # 服务地址
    NACOS_REG_SERVICE_PORT = 'application.nacos.registration.service-port'  # 服务端口
    NACOS_REG_CLUSTER_NAME = 'application.nacos.registration.cluster-name'  # 集群名称(可选)
    NACOS_REG_WEIGHT = 'application.nacos.registration.weight'  # 权重
    NACOS_REG_HEARTBEAT_INTERVAL = 'application.nacos.registration.heartbeat-interval'  # 心跳信号间隔

class EnableNacos(ApplicationContextPlugin):
    """ 启用nacos注册中心，启用之后服务在启动时会被自动注册到nacos注册中心 """
    def modify_config_schema(self, schema: dict):
        """ 初始化nacos相关的配置拓展 """
        schema['application']['schema']['nacos'] = {
            'type': 'dict',
            'schema': {
                'server-addr': {'type': 'string', 'default': 'localhost'},  # nacos服务所在地址
                'server-port': {'type': 'integer', 'default': '8848'},
                'registration': {  # 服务注册
                    'type': 'dict',
                    'schema': {
                        'service-name': {'type': 'string', 'default': 'undefined'},  # 服务名称
                        'service-addr': {'type': 'string', 'default': '127.0.0.1'},  # 服务地址
                        'service-port': {'type': 'integer', 'default': 5000},  # 服务端口
                        'cluster-name': {'type': 'string', 'default': 'undefined'},  # 集群名称
                        'weight': {'type': 'integer', 'default': 1},
                        'heartbeat-interval': {'type': 'integer', 'default': 5}
                    }
                },
            }
        }

    def plugin_setup(self, ctx: T):
        """ nacos插件初始化 """
        self.init_nacos_client(ctx)  # 初始化nacos客户端
        self.register_nacos_service(ctx)  # 将服务实例注册进入nacos
        self.start_heartbeat(ctx)

    @staticmethod
    def init_nacos_client(ctx: T):
        """ 初始化nacos """
        ctx.logger.info(f'nacos enabled for application context [{ctx.namespace}]')
        nacos_server_addr = ctx.config.get(NacosConfigKey.NACOS_SERVER_ADDR)
        nacos_server_port = ctx.config.get(NacosConfigKey.NACOS_SERVER_PORT)

        from nacos import NacosClient
        ctx.nacos_client = NacosClient(
            f'{nacos_server_addr}:{nacos_server_port}',
            namespace='public',
        )  # 初始化nacos客户端实例

    @staticmethod
    def register_nacos_service(ctx: T):
        service_name = ctx.config.get(NacosConfigKey.NACOS_REG_SERVICE_NAME)  # 服务名称
        service_addr = ctx.config.get(NacosConfigKey.NACOS_REG_SERVICE_ADDR)
        service_port = ctx.config.get(NacosConfigKey.NACOS_REG_SERVICE_PORT)
        cluster_name = ctx.config.get(NacosConfigKey.NACOS_REG_CLUSTER_NAME)
        weight = ctx.config.get(NacosConfigKey.NACOS_REG_WEIGHT)

        ctx.nacos_client.add_naming_instance(
            service_name=service_name,
            ip=service_addr,
            port=service_port,
            cluster_name=cluster_name,
            weight=weight,
        )

        ctx.logger.info(ctx.nacos_client.list_naming_instance(service_name='undefined'))

    @staticmethod
    def start_heartbeat(ctx: T):
        """ 启动心跳信号线程 """
        import time
        import threading

        ctx.heartbeat_running = True
        service_name = ctx.config.get(NacosConfigKey.NACOS_REG_SERVICE_NAME)  # 服务名称
        service_addr = ctx.config.get(NacosConfigKey.NACOS_REG_SERVICE_ADDR)
        service_port = ctx.config.get(NacosConfigKey.NACOS_REG_SERVICE_PORT)
        heartbeat_interval = ctx.config.get(NacosConfigKey.NACOS_REG_HEARTBEAT_INTERVAL)

        def thread_target():
            while ctx.heartbeat_running:
                try:
                    ctx.nacos_client.send_heartbeat(
                        service_name=service_name,
                        ip=service_addr,
                        port=service_port
                    )
                except Exception as e:
                    ctx.logger.error(f"failed to send heartbeat: {e}")
                time.sleep(heartbeat_interval)

        ctx.heartbeat_thread = threading.Thread(target=thread_target)
        ctx.heartbeat_thread.daemon = True
        ctx.heartbeat_thread.start()


class SwaggerConfigKey:
    SWAGGER_TITLE = 'application.swagger.title'
    SWAGGER_UIVERSION = 'application.swagger.uiversion'
    SWAGGER_DESCRIPTION = 'application.swagger.description'
    SWAGGER_VERSION = 'application.swagger.version'
    SWAGGER_TERMS_OF_SERVICE = 'application.swagger.terms-of-service'
    SWAGGER_CONTACT_NAME = 'application.swagger.contact.name'
    SWAGGER_CONTACT_EMAIL = 'application.swagger.contact.email'
    SWAGGER_CONTACT_URL = 'application.swagger.contact.url'
    SWAGGER_LICENSE_NAME = 'application.swagger.license.name'
    SWAGGER_LICENSE_URL = 'application.swagger.license.url'

class EnableSwagger(ApplicationContextPlugin):
    """ 启用Swagger，依赖注释自动生成接口文档 """
    priority = -1
    def modify_config_schema(self, schema: dict):
        schema['application']['schema']['swagger'] = {
            'type': 'dict',
            'schema': {
                'title': {'type': 'string', 'default': 'undefined'},  # swagger文档标题
                'uiversion': {'type': 'integer', 'default': 3},  # ui界面版本
                'description': {'type': 'string', 'default': 'undefined'},  # 文档描述信息
                'version': {'type': 'string', 'default': '1.0.0'},  # 文档版本
                'terms-of-service': {'type': 'string', 'default': 'undefined'},  # 帮助文档页面
                'contact': {  # 联系方式
                    'type': 'dict',
                    'schema': {
                        'name': {'type': 'string', 'default': 'undefined'},  # 作者名
                        'email': {'type': 'string', 'default': 'undefined'},  # 作者邮箱
                        'url': {'type': 'string', 'default': 'undefined'},  # 项目链接
                    }
                },
                'license': {  # 证书
                    'type': 'dict',
                    'schema': {
                        'name': {'type': 'string', 'default': 'MIT'},  # 协议
                        'url': {'type': 'string', 'default': 'https://opensource.org/licenses/MIT'},  # 协议链接
                    }
                },
            }
        }

    def plugin_setup(self, ctx: T):
        """ 初始化项目接口文档(flasgger) """
        dev_mode = ctx.config.get(DefaultConfigKey.APP_DEV_MODE)
        if not dev_mode: return  # 仅在开发者模式下开启swagger文档

        from flasgger import Swagger
        swagger_config = {  # swagger初始化
            "title": ctx.config.get(SwaggerConfigKey.SWAGGER_TITLE),
            "uiversion": ctx.config.get(SwaggerConfigKey.SWAGGER_UIVERSION),
            "description": ctx.config.get(SwaggerConfigKey.SWAGGER_DESCRIPTION),
            "version": ctx.config.get(SwaggerConfigKey.SWAGGER_VERSION),
            "termsOfService": ctx.config.get(SwaggerConfigKey.SWAGGER_TERMS_OF_SERVICE),
            "contact": {
                "name": ctx.config.get(SwaggerConfigKey.SWAGGER_CONTACT_NAME),
                "email": ctx.config.get(SwaggerConfigKey.SWAGGER_CONTACT_EMAIL),
                "url": ctx.config.get(SwaggerConfigKey.SWAGGER_CONTACT_URL)
            },
            "license": {
                "name": ctx.config.get(SwaggerConfigKey.SWAGGER_LICENSE_NAME),
                "url": ctx.config.get(SwaggerConfigKey.SWAGGER_LICENSE_URL)
            }
        }
        ctx.app.config['SWAGGER'] = swagger_config
        Swagger(ctx.app)


class DiscordBotContextV1:
    """ discord机器人服务上下文，用于快速构建机器人实例 """
    