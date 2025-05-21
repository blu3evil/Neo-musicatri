from __future__ import annotations

import gettext
from abc import abstractmethod

resource_schema = {
    # 应用信息配置
    'environment': {'type': 'string', 'default': 'global'},
    'active-environment': {'type': 'string', 'default': 'global'},
    'application': {
        'type': 'dict',
        'schema': {
            'dev-mode': {'type': 'boolean', 'default': False},  # 是否开启dev模式
            'information': {
                'type': 'dict',
                'schema': {
                    'name': {'type': 'string', 'default': 'undefined'},
                    'version': {'type': 'string', 'default': '1.0.0'},
                    'description': {'type': 'string', 'default': 'undefined auth_client.py'},
                }
            },
            'logging': {  # 日志配置
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
                            'formatter': {'type': 'string', 'default': 'default'},
                        }
                    },
                    'filelog-logging': {
                        'type': 'dict',
                        'schema': {
                            'enable': {'type': 'boolean', 'default': False},
                            'level': {'type': 'string', 'default': 'DEBUG'},
                            'extname': {'type': 'string', 'default': ''},
                            'file-directory': {'type': 'string', 'default': 'logs'},  # /temp/logs
                            'formatter': {'type': 'string', 'default': 'default'},
                        }
                    }
                }
            }
        }
    }
}

class ResourceContextConfigKey:
    # 应用配置
    DEV_MODE = 'application.dev-mode'
    LANGUAGE = 'application.language'
    INFO_NAME = 'application.information.name'
    INFO_VERSION = 'application.information.version'
    INFO_DESCRIPTION = 'application.information.description'

    # 日志配置
    LOG_PRINT_BANNER = 'application.logging.print-banner'
    LOG_DEFAULT_LOGGING_ENABLE = 'application.logging.default-logging.enable'
    LOG_DEFAULT_LOGGING_LEVEL = 'application.logging.default-logging.level'
    LOG_CONSOLE_LOGGING_ENABLE = 'application.logging.console-logging.enable'
    LOG_CONSOLE_LOGGING_LEVEL = 'application.logging.console-logging.level'
    LOG_CONSOLE_LOGGING_FORMATTER = 'application.logging.console-logging.formatter'
    LOG_FILELOG_LOGGING_ENABLE = 'application.logging.filelog-logging.enable'
    LOG_FILELOG_LOGGING_LEVEL = 'application.logging.filelog-logging.level'
    LOG_FILELOG_LOGGING_FILE_DIRECTORY = 'application.logging.filelog-logging.file-directory'
    LOG_FILELOG_LOGGING_FORMATTER = 'application.logging.filelog-logging.formatter'


class WebApplicationContextConfigKey:
    # 密匙配置
    SECURITY_SECRET_KEY = 'application.security.secret-key'
    SECURITY_OAUTH_INSECURE_TRANSPORT = 'application.security.oauth.insecure-transport'
    SECURITY_OAUTH_RELAX_TOKEN_SCOPE = 'application.security.oauth.insecure-transport'

    # WSGI服务器配置
    WSGI_HOST = 'application.wsgi-server.host'
    WSGI_PORT = 'application.wsgi-server.port'
    WSGI_WERKZEUG_DEBUG_MODE = 'application.wsgi-server.werkzeug.debug-mode'
    WSGI_WERKZEUG_LOG_OUTPUT = 'application.wsgi-server.werkzeug.log-output'
    WSGI_WERKZEUG_USE_RELOADER = 'application.wsgi-server.werkzeug.use-reloader'
    WSGI_GUNICORN_WORKERS = 'application.wsgi-server.gunicorn.workers'
    WSGI_GUNICORN_THREADS = 'application.wsgi-server.gunicorn.threads'
    WSGI_GUNICORN_DAEMON = 'application.wsgi-server.gunicorn.daemon'
    WSGI_GUNICORN_WORKER_CLASS = 'application.wsgi-server.gunicorn.worker-class'
    WSGI_GUNICORN_WORKER_CONNECTIONS = 'application.wsgi-server.gunicorn.worker-connections'
    WSGI_GUNICORN_PIDFILE = 'application.wsgi-server.gunicorn.pidfile'
    WSGI_GUNICORN_ACCESSLOG = 'application.wsgi-server.gunicorn.accesslog'
    WSGI_GUNICORN_ERRORLOG = 'application.wsgi-server.gunicorn.errorlog'
    WSGI_GUNICORN_LOGLEVEL = 'application.wsgi-server.gunicorn.loglevel'

import logging
import os, os.path as path

from common import root_path
from common.utils.config import Config, ConfigSchemaBuilder
from common.utils.locale import DefaultLocaleFactory
from common.utils.logger import SimpleLoggerFacade

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


from typing import Callable, Optional
from pathlib import Path
from typing import Type, TypeVar

class InitHook:
    """ 初始化钩子 """
    func: Callable
    def __init__(self, func: Callable):
        self.func = func

    def init(self):
        self.func()

U = TypeVar('U', bound=DefaultLocaleFactory)  # LocaleFactory及其子类
class ResourceContext:
    """
    资源上下文，资源上下文具有基础的资源，例如配置、本地化以及日志，每个资源上下文以命名空间（namespace）相互独立
    资源默认分布在对应的资源目录中，例如配置默认分布于/config目录下，本地化分布于/resources/{namespace}/locale下
    日志则分布于/temp/logs目录下

    配置： 通过传入日志配置校验config_schema来设定上下文的配置校验
    本地化：资源上下文可以通过读取.po .mo文件实现本地化
    日志：资源上下文具备基础的记录日志能力
    """
    namespace: str  # 命名空间
    config_schema: dict  # 配置文件校验规则
    config_schema_builder: ConfigSchemaBuilder  # 配置文件规则校验构建器

    config: Config  # 配置
    logger: logging.Logger  # 日志
    boot_logger: logging.Logger  # 启动日志

    pre_init_hooks: list[InitHook]
    on_init_hooks: list[InitHook]
    post_init_hooks: list[InitHook]

    def __init__(self, namespace):
        self.namespace = namespace
        self.config_schema = resource_schema
        self.config_schema_builder = ConfigSchemaBuilder(origin=resource_schema)

        self._init_boot_logger()  # 初始化启动日志
        self._load_init_hook()  # 加载初始化钩子

    def _load_init_hook(self):
        def _walk_through_mro(hook_name: str, hook_list: list[InitHook]):
            # MRO 反向遍历，确保 BaseClass 的 pre_init 先执行
            for cls in reversed(self.__class__.__mro__):
                if hook_name in cls.__dict__:
                    method = cls.__dict__[hook_name]
                    hook: InitHook = method(self)
                    if hook is not None:
                        hook_list.append(hook)

        self.pre_init_hooks = []
        self.on_init_hooks = []
        self.post_init_hooks = []

        # 加载初始化钩子
        _walk_through_mro('pre_init', self.pre_init_hooks)
        _walk_through_mro('on_init', self.on_init_hooks)
        _walk_through_mro('post_init', self.post_init_hooks)


    def _init_config(self):
        """ 初始化配置，配置文件路径位于/config/${namespace}.yaml """
        self.config = Config(self.config_file_path, self.config_schema_builder.build())  # 项目配置
        self.config.load()  # 加载配置

    def _init_logger(self):
        """ 初始化日志 """
        facade = SimpleLoggerFacade(name=self.namespace)  # 日志配置
        facade.set_default(self.config.get(ResourceContextConfigKey.LOG_DEFAULT_LOGGING_LEVEL))

        # 初始化控制台日志
        if self.config.get(ResourceContextConfigKey.LOG_CONSOLE_LOGGING_ENABLE):
            facade.set_console(
                level=self.config.get(ResourceContextConfigKey.LOG_CONSOLE_LOGGING_LEVEL),
                formatter=self.config.get(ResourceContextConfigKey.LOG_CONSOLE_LOGGING_FORMATTER)
            )

        # 初始化文件日志
        if self.config.get(ResourceContextConfigKey.LOG_FILELOG_LOGGING_ENABLE):
            logs_directory = str(
                self.temp_directory_path /
                self.config.get(ResourceContextConfigKey.LOG_FILELOG_LOGGING_FILE_DIRECTORY)
            )  # 日志文件创建目录

            extname = self.namespace
            facade.set_filelog(
                level=self.config.get(ResourceContextConfigKey.LOG_FILELOG_LOGGING_LEVEL),
                logs_directory=logs_directory,
                ext=extname,
                formatter=self.config.get(ResourceContextConfigKey.LOG_FILELOG_LOGGING_FORMATTER)
            )  # 日志文件创建位置
        self.logger = facade.get_logger()  # 默认日志

        enable_logger = self.config.get(ResourceContextConfigKey.LOG_DEFAULT_LOGGING_ENABLE)
        self.logger.disabled = not enable_logger  # 禁用日志输出

    def _init_boot_logger(self):
        """
        初始化启动日志，启动日志用于在上下文启动阶段记录日志信息，对于外部不应使用此日志记录器
        """
        facade = SimpleLoggerFacade(name=f'{self.namespace}.boot')  # 日志配置
        facade.set_default(level='DEBUG')
        facade.set_console(level='DEBUG', formatter='background-render')
        self.boot_logger = facade.get_logger()
        self.boot_logger.disabled = not self.enable_boot_logger()

    def pre_init(self) -> InitHook:
        """ 预初始化方法，此方法在所有初始化函数之前调用 """

    def post_init(self) -> InitHook:
        """ 后初始化方法，此方法在所有初始化函数之后调用 """

    def on_init(self) -> InitHook:
        """
        子类可以覆写此方法自定义自身需要的初始化步骤，上下文在使用时会通过initialize执行初始化
        """
        def hook_func():
            self._init_config()  # 初始化配置
            self._init_logger()  # 初始化日志
        return InitHook(hook_func)

    @staticmethod
    def ensure_file(target_path: Path):
        """ 确保文件存在，如果文件不存在，那么创建这个文件 """
        if not target_path.exists():  # 文件不存在，创建它
            target_path.parent.mkdir(parents=True, exist_ok=True)  # 确保父目录存在
            target_path.touch(exist_ok=True)  # 创建空文件
        elif not target_path.is_file():
            # 如果路径存在但不是文件，抛出异常
            raise ValueError(f"{target_path} exists but is not a regular file")

    @staticmethod
    def ensure_directory(target_path: Path):
        """ 确保目录存在，如果目录不存在，那么创建它 """
        if not target_path.exists():  # 目录不存在
            target_path.mkdir(parents=True, exist_ok=True)
        elif not target_path.is_dir():
            # 如果路径存在但不是目录，抛出异常
            raise ValueError(f"{target_path} exists but is not a regular directory")

    def ensure_resource_directory(self, target_path: Path):
        """
        确保资源路径存在，如果不存在，那么创建它，例如你可以传入Path(songcache)，那么此方法会尝试创建
        /resources/{namespace}/songcache目录
        """
        resource_path = self.resource_directory_path
        self.ensure_directory(resource_path / target_path)

    def ensure_temp_directory(self, target_path: Path):
        """
        确保临时目录下目录存在，如果不存在，那么创建它，例如你可以传入Path(songcache)，之后此方法
        会尝试创建/temp/{namespace}/songcache目录
        """
        temp_path = self.temp_directory_path
        self.ensure_directory(temp_path / target_path)

    def exec_pre_init_hooks(self):
        self.boot_logger.debug(f'setup [{self.namespace}] pre init hooks')
        for hook in self.pre_init_hooks:
            hook.init()  # 预初始化钩子

    def exec_on_init_hooks(self):
        self.boot_logger.debug(f'setup [{self.namespace}] on init hooks')
        for hook in self.on_init_hooks:
            hook.init()  # 预初始化钩子

    def exec_post_init_hooks(self):
        self.boot_logger.debug(f'setup [{self.namespace}] post init hooks')
        for hook in self.post_init_hooks:
            hook.init()  # 后初始化钩子

    def initialize(self):
        """ 初始化的实际执行方法 """
        self.exec_pre_init_hooks()
        self.exec_on_init_hooks()
        self.exec_post_init_hooks()

    def enable_boot_logger(self) -> bool:
        """ 选择是否启用boot_logger """
        return True

    @property
    def resource_directory_path(self) -> Path:
        """
        返回当前上下文的资源目录路径，此路径返回后将会包含上下文的namespace，例如ServerAuthContext将会返回
        /resources/server-auth/...
        """
        return Path(root_path) / 'resources' / self.namespace

    @property
    def temp_directory_path(self) -> Path:
        """
        返回当前服务上下文的临时文件目录路径，此路径返回后将会包含上下文的namespace，例如ServerAuthContext将会返回
        /temp/server-auth/...
        """
        return Path(root_path) / 'temp' / self.namespace

    @property
    def config_file_path(self) -> Path:
        """
        返回当前服务上下文的配置文件路径，此路径返回后将会包含上下文的namespace，例如ServerAuthContext将会返回
        /config/auth-server.yaml
        """
        return Path(root_path) / 'config' / f'{self.namespace}.yaml'


from enum import Enum, auto
class InitPhase(Enum):
    """ 插件初始化阶段 """
    BEFORE_PRE_INIT = auto()  # pre_init执行前后
    AFTER_PRE_INIT = auto()
    BEFORE_ON_INIT = auto()  # on_init执行前后
    AFTER_ON_INIT = auto()
    BEFORE_POST_INIT = auto()  # post_init执行前后
    AFTER_POST_INIT = auto()


T = TypeVar('T', bound=ResourceContext)
from collections import defaultdict
from typing import DefaultDict
class PluginHookManager:
    """ 插件钩子函数管理器，用于组织管理插件初始化 """
    def __init__(self, ctx: T):
        self.ctx = ctx  # 当前上下文
        self._hooks: DefaultDict[InitPhase, list[InitHook]] = defaultdict(list)

    def _register_hook(self, phase: InitPhase, hook: InitHook):
        """ 在特定阶段注册插件钩子 """
        if hook: self._hooks[phase].append(hook)

    def register_plugin(self, plugin: ContextPlugin):
        """ 注册插件 """
        self._register_hook(InitPhase.BEFORE_PRE_INIT, plugin.before_pre_init(self.ctx))
        self._register_hook(InitPhase.AFTER_PRE_INIT, plugin.after_pre_init(self.ctx))
        self._register_hook(InitPhase.BEFORE_ON_INIT, plugin.before_on_init(self.ctx))
        self._register_hook(InitPhase.AFTER_ON_INIT, plugin.after_on_init(self.ctx))
        self._register_hook(InitPhase.BEFORE_POST_INIT, plugin.before_post_init(self.ctx))
        self._register_hook(InitPhase.AFTER_POST_INIT, plugin.after_post_init(self.ctx))

    def setup_hook(self, phase: InitPhase):
        """ 执行特定阶段的初始化钩子函数 """
        for hook in self._hooks[phase]:
            hook.init()

class PluginSupportMixin:
    """ 插件混入支持，通过继承此类来让类支持插件注册 """
    _plugin_manager: PluginHookManager  # 上下文插件注册表

    # noinspection PyTypeChecker
    def __init__(self, namespace):
        if not isinstance(self, ResourceContext):
            raise TypeError(f'{self.__class__} is not a subclass of ResourceContext')

        super().__init__(namespace)  # 调用父级初始化函数
        self._plugin_manager = PluginHookManager(self)  # 初始化插件管理器

    # noinspection PyUnresolvedReferences
    def register_plugin(self, plugin: ContextPlugin):
        """ 注册插件 """
        self.boot_logger.debug(f'register plugin [{plugin.plugin_id}] for [{self.namespace}]')
        self._plugin_manager.register_plugin(plugin)

    def _setup_hook(self, phase: InitPhase):
        """ 执行特定阶段的初始化钩子 """
        self._plugin_manager.setup_hook(phase)

    # noinspection PyUnresolvedReferences
    def initialize(self):
        """ 覆写父类ResourceContext的initialize初始化函数，实现注入插件初始化片段 """
        self._setup_hook(InitPhase.BEFORE_PRE_INIT)
        self.exec_pre_init_hooks()  # 执行pre_init
        self._setup_hook(InitPhase.AFTER_PRE_INIT)

        self._setup_hook(InitPhase.BEFORE_ON_INIT)
        self.exec_on_init_hooks()
        self._setup_hook(InitPhase.AFTER_ON_INIT)

        self._setup_hook(InitPhase.BEFORE_POST_INIT)
        self.exec_post_init_hooks()
        self._setup_hook(InitPhase.AFTER_POST_INIT)


class ContextPlugin:
    """ 上下文插件父类，通过继承上下文插件类来实现为服务上下文编写拓展插件 """
    priority = -1  # 优先级，平衡时的优先决策
    plugin_id: str  # 插件唯一标识符  todo: 完善插件id合法性判断，避免重复插件id
    depends_on: list[str] = []  # 插件所需依赖 todo: 完善依赖树处理

    def __init__(self, plugin_id):
        if not plugin_id:
            raise RuntimeError('illegal plugin_id')
        self.plugin_id = plugin_id

    def before_pre_init(self, ctx: T) -> InitHook:
        """ pre_init之前执行的初始化逻辑 """

    def after_pre_init(self, ctx: T) -> InitHook:
        """ pre_init之后执行的初始化逻辑 """

    def before_on_init(self, ctx: T) -> InitHook:
        """ on_init之前执行的初始化逻辑 """

    def after_on_init(self, ctx: T) -> InitHook:
        """ on_init之后执行的初始化逻辑 """

    def before_post_init(self, ctx: T) -> InitHook:
        """ post_init之前执行的初始化逻辑 """

    def after_post_init(self, ctx: T) -> InitHook:
        """ post_init之后执行的初始化逻辑 """

    def __call__(self, ctx: Type[T]):
        if not issubclass(ctx, PluginSupportMixin):
            # 需要类使用PluginSupportMixin混入之后才可使用插件功能
            raise TypeError(f'{ctx} is not a subclass of PluginSupportMixin')

        plugin_self = self
        class EnhancedContext(ctx):
            # noinspection PyArgumentList
            def __init__(self):
                super(EnhancedContext, self).__init__()
                self.register_plugin(plugin_self)  # 注册插件
        return EnhancedContext

class EnableI18N(ContextPlugin):
    """ 启用本地化 """
    factory_supplier: Callable[[str, Path, str], U]  # 工厂供应商，提供本地化实例

    def __init__(self, factory_supplier: Callable[[str, Path, str], U]=None):
        self.factory_supplier = factory_supplier
        super().__init__('enable_i18n')

    def before_pre_init(self, ctx: T) -> InitHook:
        def hook_func():
            ctx.config_schema_builder.set_at_path(
                'application.language',
                {'type': 'string', 'default': 'en-US'})
        return InitHook(hook_func)

    def after_on_init(self, ctx: T) -> InitHook:
        def hook_func():
            locale_dir = ctx.resource_directory_path / 'locales'
            default_language = ctx.config.get(ResourceContextConfigKey.LANGUAGE)  # 默认语言

            if self.factory_supplier: ctx.locale = self.factory_supplier(ctx.namespace, locale_dir, default_language)
            else: ctx.locale = DefaultLocaleFactory(ctx.namespace, locale_dir, default_language)
        return InitHook(hook_func)


class WebApplicationContext(ResourceContext):
    """
    web服务应用上下文，基于资源上下文ResourceContext，web服务应用上下文同样具备配置，本地化，日志输出的
    基础能力，基于此web服务应用上下文通过封装flask服务实例提供了更灵活便捷的用法

    提供插件能力，可以通过注解来自定义开启flask session、nacos等功能，可以快速完成单体服务实例的开发
    """
    app: Flask  # web应用
    banner: str  # 旗帜
    locale: Optional[U]  # 本地化

    def on_init(self) -> InitHook:
        def hook_func():
            self.init_flask_app()  # 初始化flask
            self.init_oauthlib()  # 初始化oauthlib
            self.init_exception_handlers()  # 初始化异常处理器
            self.print_banner()  # 打印旗帜
        return InitHook(hook_func)

    def pre_init(self) -> InitHook:
        def hook_func():
            self.config_schema_builder.set_at_path('application.security', {
                'type': 'dict',
                'schema': {
                    'secret-key': {'type': 'string', 'default': 'undefined'},
                    'oauth': {
                        'type': 'dict',
                        'schema': {
                            'insecure-transport': {'type': 'boolean', 'default': False},  # 允许在HTTP下执行oauth
                            'relax-token-scope': {'type': 'boolean', 'default': False},  # 允许动态调整oauth申请权限
                        }
                    }
                }
            }).set_at_path('application.wsgi-server', {
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
                    }
                }
            })
        return InitHook(hook_func)

    def init_flask_app(self):
        """ 初始化flask app """
        dev_mode = self.config.get(ResourceContextConfigKey.DEV_MODE)
        if dev_mode: self.logger.warning(
            "dev mode is enabled, know more about development mode at README.md, this mode is only used for "
            "development and testing, do not enable this mode in production environment")

        self.app = Flask(self.namespace)  # app实例
        secret_key = self.config.get(WebApplicationContextConfigKey.SECURITY_SECRET_KEY)
        self.app.config['SECRET_KEY'] = secret_key  # 应用密钥配置

    def init_oauthlib(self):
        """ 初始化oauth lib """
        if self.config.get(WebApplicationContextConfigKey.SECURITY_OAUTH_INSECURE_TRANSPORT):
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # 仅https下的oath

        if self.config.get(WebApplicationContextConfigKey.SECURITY_OAUTH_RELAX_TOKEN_SCOPE):
            os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'  # 允许oauth2动态权限调整

    def init_exception_handlers(self):
        """ 初始化项目异常处理器 """
        # 注册异常拦截器，不会覆盖原始异常
        def register_errorhandler(status, error_consumer):
            @self.app.errorhandler(status)
            def handler(e):
                _ = self._safe_gettext()
                self.logger.error(e)  # 记录日志
                response = error_consumer(e, _)
                response.status_code = status
                return response

        register_errorhandler(400, lambda e, _: jsonify({'message': _('Bad Request')}))
        register_errorhandler(401, lambda e, _: jsonify({'message': _('Unauthorized')}))
        register_errorhandler(403, lambda e, _: jsonify({'message': _('Forbidden')}))
        register_errorhandler(404, lambda e, _: jsonify({'message': _('NotFound')}))
        register_errorhandler(500, lambda e, _: jsonify({'message': _('Internal Server Error')}))

        dev_mode = self.config.get(ResourceContextConfigKey.DEV_MODE)
        if dev_mode: return  # 开发者模式下并不会注册这一项

        @self.app.errorhandler(Exception)
        def handle_uncaught(e: Exception) -> Response:
            _ = self._safe_gettext()
            # todo: 此处向开发者提交未知异常消息，记录错误日志信息
            self.logger.error(_("unknown: %s") % e)
            response = jsonify({'message': str(e)})
            response.status_code = 400  # 将异常原因归咎于用户
            return response

    def print_banner(self):
        """ 打印旗帜 """
        if self.config.get(ResourceContextConfigKey.LOG_PRINT_BANNER):
            self.logger.info(self.banner)

    def run_werkzeug(self):
        """ 使用werkzeug启动flask """
        host = self.config.get(WebApplicationContextConfigKey.WSGI_HOST)  # 服务器主机名
        port = self.config.get(WebApplicationContextConfigKey.WSGI_PORT)  # 服务器端口号
        debug_mode = self.config.get(WebApplicationContextConfigKey.WSGI_WERKZEUG_DEBUG_MODE)  # 调试模式
        log_output = self.config.get(WebApplicationContextConfigKey.WSGI_WERKZEUG_LOG_OUTPUT)  # 是否打印flask日志
        use_reloader = self.config.get(WebApplicationContextConfigKey.WSGI_WERKZEUG_USE_RELOADER)  # 使用热重载

        self.app.run(
            host=host,
            port=port,
            debug=debug_mode,
            use_reloader=use_reloader,
        )

    def _safe_gettext(self) -> gettext:
        if hasattr(self, 'locale'):
            return self.locale.get()
        return gettext.gettext


class EnableApiAspect(ContextPlugin):
    """ 启用api切面编程 """
    def __init__(self):
        super().__init__('enable_api_aspect')

    def after_on_init(self, ctx: T) -> InitHook:
        def hook_func():
            from common.aop.api_aspect import ApiAspect
            ctx.aspect = ApiAspect(ctx)
        return InitHook(hook_func)


class EnableGunicorn(ContextPlugin):
    """ 启用gunicorn，启用此项之后可以使用gunicorn_config属性获取gunicorn启动配置项 """
    def __init__(self):
        super().__init__('enable_gunicorn')

    def before_pre_init(self, ctx: T) -> InitHook:
        def hook_func():
            ctx.config_schema_builder.set_at_path('application.wsgi-server.gunicorn', {
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
            })
        return InitHook(hook_func)

    def after_post_init(self, ctx: T) -> InitHook:
        def hook_func():
            gunicorn_config = GunicornConfig()
            """ gunicorn上下文，包含gunicorn配置项 """
            gunicorn_config.workers = ctx.config.get(WebApplicationContextConfigKey.WSGI_GUNICORN_WORKERS)  # 进程数
            gunicorn_config.threads = ctx.config.get(WebApplicationContextConfigKey.WSGI_GUNICORN_THREADS)  # 线程数
            gunicorn_config.bind = f'{ctx.config.get(WebApplicationContextConfigKey.WSGI_HOST)}:{ctx.config.get(WebApplicationContextConfigKey.WSGI_PORT)}'  # 端口ip
            gunicorn_config.daemon = ctx.config.get(WebApplicationContextConfigKey.WSGI_GUNICORN_DAEMON)  # 是否后台运行
            gunicorn_config.worker_class = ctx.config.get(WebApplicationContextConfigKey.WSGI_GUNICORN_WORKER_CLASS)  # 工作模式协程
            gunicorn_config.worker_connections = ctx.config.get(
                WebApplicationContextConfigKey.WSGI_GUNICORN_WORKER_CONNECTIONS)  # 最大连接数（并发量）

            # todo: 修复gunicorn启动时的pidfile accesslog errorlog配置问题
            gunicorn_config.pidfile = str(ctx.temp_directory_path / ctx.config.get(
                WebApplicationContextConfigKey.WSGI_GUNICORN_PIDFILE))  # gunicorn进程文件'/var/run/gunicorn.pid'
            gunicorn_config.accesslog = str(ctx.temp_directory_path / ctx.config.get(
                WebApplicationContextConfigKey.WSGI_GUNICORN_ACCESSLOG))  # 设置访问日志和错误信息日志路径'/var/log/gunicorn_access.log'
            gunicorn_config.errorlog = str(ctx.temp_directory_path / ctx.config.get(
                WebApplicationContextConfigKey.WSGI_GUNICORN_ERRORLOG))  # '/var/log/gunicorn_error.log'
            gunicorn_config.loglevel = ctx.config.get(WebApplicationContextConfigKey.WSGI_GUNICORN_LOGLEVEL)  # 设置日志记录水平 warning
            ctx.gunicorn_config = gunicorn_config
        return InitHook(hook_func)


class CorsConfigKey:
    SECURITY_CORS_ALLOW_ORIGINS = 'application.security.cors.allow-origins'
    SECURITY_CORS_ALLOW_HEADERS = 'application.security.cors.allow-headers'
    SECURITY_CORS_ALLOW_METHODS = 'application.security.cors.allow-methods'
    SECURITY_CORS_SUPPORTS_CREDENTIALS = 'application.security.cors.supports-credentials'


class EnableCors(ContextPlugin):
    """ 启用cors """
    def __init__(self):
        super().__init__('enable_cors')

    def before_pre_init(self, ctx: T) -> InitHook:
        def hook_func():
            ctx.config_schema_builder.set_at_path('application.security.cors', {
                'type': 'dict',
                'schema': {
                    'allow-origins': {'type': 'list', 'default': ['http://localhost:5173']},
                    'allow-headers': {'type': 'list', 'default': ['Content-Type', 'Authorization', 'Accept-Language']},
                    'allow-methods': {'type': 'list', 'default': ['GET', 'POST', 'PUT', 'DELETE', 'TRACE']},
                    'supports-credentials': {'type': 'boolean', 'default': True},
                }
            })
        return InitHook(hook_func)

    def after_post_init(self, ctx: T) -> InitHook:
        def hook_func():
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
        return InitHook(hook_func)


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


class SessionEnhance(ContextPlugin):
    """ 会话增强 """
    def __init__(self):
        super().__init__('session_enhance')

    def before_pre_init(self, ctx: T) -> InitHook:
        def hook_func():
            ctx.config_schema_builder.set_at_path('application.session', {
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
            })
        return InitHook(hook_func)

    def after_on_init(self, ctx: T) -> InitHook:
        def hook_func():
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
            ctx.app.config['SESSION_COOKIE_SAMESITE'] = ctx.config.get(
                SessionConfigKey.SESSION_COOKIE_SAMESITE)  # 会话同源策略
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
        return InitHook(hook_func)

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


class EnableCache(ContextPlugin):
    """ 启用缓存 """
    def __init__(self):
        super().__init__('enable_cache')

    def before_pre_init(self, ctx: T) -> InitHook:
        def hook_func():
            ctx.config_schema_builder.set_at_path('application.cache', {
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
            })
        return InitHook(hook_func)

    def after_on_init(self, ctx: T) -> InitHook:
        def hook_func():
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
        return InitHook(hook_func)


class EnableJWT(ContextPlugin):
    """ 启用jwt """
    def __init__(self):
        super().__init__('enable_jwt')

    def after_on_init(self, ctx: T) -> InitHook:
        def hook_func():
            from flask_jwt_extended import JWTManager
            secret_key = ctx.config.get(WebApplicationContextConfigKey.SECURITY_SECRET_KEY)
            ctx.app.config['JWT_SECRET_KEY'] = secret_key
            ctx.app.config['JWT_BLACKLIST_ENABLED'] = True
            ctx.app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']  # 检查访问令牌和刷新令牌
            ctx.jwt = JWTManager(ctx.app)
        return InitHook(hook_func)

class DatabaseConfigKey:
    # 数据库配置
    DATABASE_DRIVER = 'application.database.driver'
    DATABASE_HOST = 'application.database.host'
    DATABASE_PORT = 'application.database.port'
    DATABASE_USERNAME = 'application.database.username'
    DATABASE_PASSWORD = 'application.database.password'
    DATABASE_DATABASE = 'application.database.database'
    DATABASE_TRACK_MODIFICATION = 'application.database.track-modification'

class EnableDatabase(ContextPlugin):
    """ 启用数据库 """
    def __init__(self):
        super().__init__('enable_database')

    def before_pre_init(self, ctx: T) -> InitHook:
        def hook_func():
            ctx.config_schema_builder.set_at_path('application.database', {
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
            })
        return InitHook(hook_func)

    def after_on_init(self, ctx: T) -> InitHook:
        def hook_func():
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
        return InitHook(hook_func)


class SocketIOConfigKey:
    SOCKETIO_CORS_ALLOW_ORIGINS = 'application.socketio.cors.allow-origins'


class EnableSocketIO(ContextPlugin):
    """ 开启socketio """
    def __init__(self):
        super().__init__('enable_socketio')

    def before_pre_init(self, ctx: T) -> InitHook:
        def hook_func():
            ctx.config_schema_builder.set_at_path('application.socketio', {
                'type': 'dict',
                'schema': {
                    'cors': {
                        'type': 'dict',
                        'schema': {
                            'allow-origins': {'type': 'list', 'default': ['http://localhost:5173']},
                        }
                    }
                }
            })
        return InitHook(hook_func)

    def after_on_init(self, ctx: T) -> InitHook:
        def hook_func():
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

        return InitHook(hook_func)


    def after_post_init(self, ctx: T) -> InitHook:
        def hook_func():

            def run_werkzeug():
                """ 覆写run_werkzeug启动流程 """
                # 覆写原始的run_werkzeug启动流程，在socketio启动时需要通过socketio实例直接启动flask
                host = ctx.config.get(WebApplicationContextConfigKey.WSGI_HOST)  # 服务器主机名
                port = ctx.config.get(WebApplicationContextConfigKey.WSGI_PORT)  # 服务器端口号
                debug_mode = ctx.config.get(WebApplicationContextConfigKey.WSGI_WERKZEUG_DEBUG_MODE)  # 调试模式
                log_output = ctx.config.get(WebApplicationContextConfigKey.WSGI_WERKZEUG_LOG_OUTPUT)  # 是否打印flask日志
                use_reloader = ctx.config.get(WebApplicationContextConfigKey.WSGI_WERKZEUG_USE_RELOADER)  # 使用热重载

                ctx.socketio.run(
                    app=ctx.app,
                    host=host,
                    port=port,
                    debug=debug_mode,
                    log_output=log_output,
                    use_reloader=use_reloader,
                    allow_unsafe_werkzeug=True
                )  # 使用werkzeug启动flask

            ctx.run_werkzeug = run_werkzeug

        return InitHook(hook_func)


class NacosConfigKey:
    NACOS_SERVER_ADDR = 'application.nacos.server-addr'  # nacos服务端地址
    NACOS_SERVER_PORT = 'application.nacos.server-port'  # nacos服务端地址
    NACOS_REG_SERVICE_NAME = 'application.nacos.registration.service-name'  # 服务名称
    NACOS_REG_SERVICE_ADDR = 'application.nacos.registration.service-addr'  # 服务地址
    NACOS_REG_SERVICE_PORT = 'application.nacos.registration.service-port'  # 服务端口
    NACOS_REG_CLUSTER_NAME = 'application.nacos.registration.cluster-name'  # 集群名称(可选)
    NACOS_REG_WEIGHT = 'application.nacos.registration.weight'  # 权重
    NACOS_REG_HEARTBEAT_INTERVAL = 'application.nacos.registration.heartbeat-interval'  # 心跳信号间隔


from functools import wraps
import inspect


class ServiceRegistry:
    def __init__(self, ctx: T):
        self.ctx = ctx
        self.namespace = 'public'
        self.group_name = "DEFAULT_GROUP"

    def get_service_address(self, service_name: str) -> Optional[str]:
        """获取服务地址（随机选择一个健康实例）"""
        try:
            instances = self.ctx.nacos_client.list_naming_instance(
                service_name,
                namespace_id=self.namespace,
                group_name=self.group_name,
                healthy_only=True
            )
            if not instances['hosts']:
                self.ctx.logger.warning(f"No healthy instance found for {service_name}")
                return None

            import random
            instance = random.choice(instances['hosts'])  # 负载均衡
            return f"http://{instance['ip']}:{instance['port']}"
        except Exception as e:
            self.ctx.logger.error(f"Failed to discover service {service_name}: {e}")
            return None

    def nacos_discover(self, service_name: str):
        """
        装饰器：从 Nacos 获取服务地址，并作为参数注入函数中
        :param service_name: Nacos 中注册的服务名
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                service_url = self.get_service_address(service_name)
                if not service_url:
                    raise RuntimeError(f"Service [{service_name}] unavailable")

                sig = inspect.signature(func)
                params = sig.parameters  # 获取被装饰函数的参数名

                if 'service_url' in params:  # 如果被装饰的方法签名包含user_id，则传递它
                    return func(*args, **kwargs, service_url=service_url)

                return func(*args, **kwargs)
            return wrapper
        return decorator



class EnableNacosDiscover(ContextPlugin):
    """ 启用服务发现，注入nacos_client实例用于服务发现 """
    def __init__(self):
        super().__init__('enable_nacos')

    def before_pre_init(self, ctx: T) -> InitHook:
        def hook_func():
            """ 初始化nacos相关的配置拓展 """
            ctx.config_schema_builder.set_at_path('application.nacos', {
                'type': 'dict',
                'schema': {
                    'server-addr': {'type': 'string', 'default': 'localhost'},  # nacos服务所在地址
                    'server-port': {'type': 'integer', 'default': '8848'},
                }
            })
        return InitHook(hook_func)

    def after_post_init(self, ctx: T) -> InitHook:
        def hook_func():
            """ nacos插件初始化 """
            self.init_nacos_client(ctx)  # 初始化nacos客户端
            self.init_service_registry(ctx)  # 初始化服务注册表
        return InitHook(hook_func)

    @staticmethod
    def init_nacos_client(ctx: T):
        """ 初始化nacos """
        nacos_server_addr = ctx.config.get(NacosConfigKey.NACOS_SERVER_ADDR)
        nacos_server_port = ctx.config.get(NacosConfigKey.NACOS_SERVER_PORT)

        from nacos import NacosClient
        ctx.nacos_client = NacosClient(
            f'{nacos_server_addr}:{nacos_server_port}',
            namespace='public',
        )  # 初始化nacos客户端实例

    @staticmethod
    def init_service_registry(ctx: T):
        ctx.service_registry = ServiceRegistry(ctx)


class EnableNacosRegister(ContextPlugin):
    """ 启用nacos注册中心，启用之后服务在启动时会被自动注册到nacos注册中心 """
    def __init__(self):
        super().__init__('enable_nacos')

    def before_pre_init(self, ctx: T) -> InitHook:
        def hook_func():
            """ 初始化nacos相关的配置拓展 """
            ctx.config_schema_builder.set_at_path('application.nacos', {
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
                    }
                }
            })
        return InitHook(hook_func)

    def after_post_init(self, ctx: T) -> InitHook:
        def hook_func():
            """ nacos插件初始化 """
            self.init_nacos_client(ctx)  # 初始化nacos客户端
            self.register_nacos_service(ctx)  # 将服务实例注册进入nacos
            self.start_heartbeat(ctx)
        return InitHook(hook_func)

    @staticmethod
    def init_nacos_client(ctx: T):
        """ 初始化nacos """
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

class EnableSwagger(ContextPlugin):
    """ 启用Swagger，依赖注释自动生成接口文档 """
    def __init__(self):
        super().__init__('enable_swagger')

    def before_pre_init(self, ctx: T) -> InitHook:
        def hook_func():
            ctx.config_schema_builder.set_at_path('application.swagger', {
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
                    }
                }
            })
        return InitHook(hook_func)

    def after_post_init(self, ctx: T) -> InitHook:
        def hook_func():
            """ 初始化项目接口文档(flasgger) """
            dev_mode = ctx.config.get(ResourceContextConfigKey.DEV_MODE)
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
        return InitHook(hook_func)


from common.domain.models import Result
from events import BotEvent
class BotState:
    """ 机器人状态 """
    def __init__(self, identify):
        self._identify = identify  # 状态标识符

    @property
    def identify(self):
        return self._identify

    def enter(self, ctx: DiscordBotContext):  # 状态变更
        """ 切入状态时的钩子函数 """
        pass

    def fadeout(self, ctx: DiscordBotContext):
        """ 切出此状态时将会触发此钩子函数 """
        pass

    def do_enter(self, ctx: DiscordBotContext):
        """ 实际切入状态时触发此钩子函数 """
        # 发布内部事件后执行切入状态钩子函数
        ctx.bot_eventbus.emit(BotEvent.STATE_CHANGE, self.identify)
        self.enter(ctx)
        # from core import socketio
        # socketio.start_background_task(target=socketio.emit, event=SocketioEvent.ATRI_STATE_CHANGE, data=self.identify, namespace='/socket/admin')
        # socketio.emit(SocketioEvent.ATRI_STATE_CHANGE, self.identify, namespace='/socket/admin')

    def do_fadeout(self, ctx: DiscordBotContext):
        """ 实际切出状态时触发此钩子函数 """
        self.fadeout(ctx)

    def start(self, ctx: DiscordBotContext) -> Result:
        """ 启动机器人 """
        return Result(500, "unsupported operation: start")

    def stop(self, ctx: DiscordBotContext) -> Result:
        """ 停止机器人 """
        return Result(500, "unsupported operation: stop")

    # 初始化，在应用启动时初始化机器人线程
    def launch(self, ctx: DiscordBotContext) -> Result:
        """ 启动机器人线程 """
        return Result(500, "unsupported operation: launch")

    # 用于线程退出的时候清理资源
    def terminate(self, ctx: DiscordBotContext) -> Result:
        """ 停止机器人线程 """
        return Result(500, "unsupported operation: terminate")


import asyncio
# 线程启动前
from threading import Thread
class BotThreadIdle(BotState):
    """ 机器人线程未启动时 """
    def __init__(self):
        super().__init__('created')

    def launch(self, ctx: DiscordBotContext) -> Result:
        def thread_target():
            ctx.bot_event_loop = asyncio.new_event_loop()  # 初始化事件循环
            asyncio.set_event_loop(ctx.bot_event_loop)  # 设置bot_thread的主事件循环
            ctx.bot_event_loop.run_forever()

        ctx.bot_thread = Thread(target=thread_target)
        ctx.bot_thread.start()
        ctx.logger.debug('bot thread start successfully')
        ctx.update_state(BotIdle())  # 机器人线程准备就绪
        return Result(200, 'start bot thread')


class BotThreadTerminated(BotState):
    """ 机器人线程终止 """
    def __init__(self):
        super().__init__('terminated')


class BotThreadTerminating(BotState):
    def __init__(self):
        super().__init__('terminating')

# 亚托莉初始化
class BotIdle(BotState):
    def __init__(self):
        super().__init__('initializing')

    def enter(self, ctx: DiscordBotContext):
        ctx.init_bot_instance()  # 初始化机器人实例
        ctx.update_state(BotStopped())  # 亚托莉准备就绪

class BotStopped(BotState):
    def __init__(self):
        super().__init__('stopped')

    def start(self, ctx: DiscordBotContext) -> Result:
        """ 启动亚托莉 """
        ctx.update_state(BotStarting())   # 切换到starting状态

        @ctx.bot_instance.event  # 启动成功回调
        async def on_ready():
            ctx.logger.info(f"bot name: {ctx.bot_instance.user}; bot id: {ctx.bot_instance.user.id}")
            ctx.bot_eventbus.emit(BotEvent.READY)
            ctx.update_state(BotStarted())  # 启动状态

        async def async_start():  # 异步启动亚托莉
            try:
                bot_token = ctx.config.get(DiscordBotContextConfigKey.BOT_TOKEN)
                await ctx.bot_instance.start(bot_token, reconnect=False)  # 启动机器人
            except Exception as e:  # 亚托莉登录失败
                ctx.bot_eventbus.emit(BotEvent.CONNECT_FAILED, str(e))  # 亚托莉启动失败
                await ctx.bot_instance.close()  # 关闭实例
                ctx.init_bot_instance()  # 重新初始化
                ctx.update_state(BotStopped())  # 恢复状态到stopped

        asyncio.run_coroutine_threadsafe(async_start(), ctx.bot_event_loop)
        return Result(200, "submit bot launching task")  # 执行亚托莉启动工作流

    def stop(self, ctx: DiscordBotContext):
        return Result(200, "bot already stopped")

    def terminate(self, ctx: DiscordBotContext):
        # ctx.bot_instance.close()  # 关闭资源
        # todo: 完善Stopped状态下的terminate方法
        pass


class BotStarted(BotState):
    """ 亚托莉已启动 """
    def __init__(self):
        super().__init__('started')

    def start(self, ctx: DiscordBotContext) -> Result:
        return Result(200, 'bot already started')

    def stop(self, ctx: DiscordBotContext) -> Result:
        """ 停止亚托莉 """
        ctx.update_state(BotStopping())   # 切换到stopping状态
        async def async_stop():  # 异步停止亚托莉
            try:
                await ctx.bot_instance.close()  # 尝试关闭亚托莉
                # ctx.bot_eventbus.emit(AtriEvent.CLOSE)
                # 切换亚托莉到初始状态
                # 机器人在调用close方法之后会话会被关闭，因此需要重新初始化机器人
                ctx.update_state(BotIdle())
            except Exception as e:  # 亚托莉退出失败
                ctx.bot_eventbus.emit(BotEvent.DISCONNECT_FAILED, str(e))
                ctx.update_state(BotStarted())  # 恢复到原始状态

        asyncio.run_coroutine_threadsafe(async_stop(), ctx.bot_event_loop)  # 停止机器人协程
        return Result(200, "submit bot shutdown task")  # 执行亚托莉停止工作流


class BotStopping(BotState):  # 正在停止
    """ 正在停止状态 """
    def __init__(self):
        super().__init__('stopping')

    def start(self, ctx: DiscordBotContext):
        raise RuntimeError('bot is still stopping')

    def stop(self, ctx: DiscordBotContext):
        return Result(400, 'musicatri is still stopping')


class BotStarting(BotState):  # 机器人正在启动
    def __init__(self):
        super().__init__('starting')


from discord import Intents
from discord.ext import commands
class BotInstance(commands.AutoShardedBot):
    """ 机器人实例 """
    def __init__(self, command_prefix: str, intents: Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)


class DiscordBotContextConfigKey:
    BOT_TOKEN = "application.bot.token"

from pyee.executor import ExecutorEventEmitter
from asyncio import AbstractEventLoop

class DiscordBotContext(ResourceContext):
    """ discord机器人服务上下文，用于快速构建机器人实例 """
    bot_token: str  # 机器人令牌

    bot_thread: Thread  # 机器人线程，基于asyncio启动事件循环
    bot_instance: BotInstance  # 机器人实例
    bot_eventbus: ExecutorEventEmitter  # 事件总线，用于在机器人内部传递事件消息
    bot_event_loop: AbstractEventLoop  # 占用机器人线程的事件循环，执行asyncio异步任务

    def __init__(self, namespace: str):
        """ 上下文初始化 """
        super().__init__(namespace=namespace)
        self.bot_eventbus = ExecutorEventEmitter()  # 事件总线
        self._state = None

    def pre_init(self) -> InitHook:
        def hook_func():
            self.config_schema_builder.set_at_path('application.bot', {
                'type': 'dict',
                'schema': {
                    'token': {'type': 'string', 'default': 'bot-token'}
                }
            })
        return InitHook(hook_func)

    def on_init(self) -> InitHook:
        def hook_func():
            self.do_init_bot_event_listener(self.bot_eventbus)  # 初始化机器人事件监听器
            self.update_state(BotThreadIdle())  # 初始化状态
        return InitHook(hook_func)

    # def init_logger(self):
    #     """ 初始化日志记录 """
    #     # todo: 完善更详细的机器人日志配置项
    #     facade = SimpleLoggerFacade(name='bot-auth_client.py-logger')  # 日志配置
    #
    #     from utils.logger import BACKGROUND_RENDER_CONSOLE_FORMATTER
    #     facade.set_default(level=logging.DEBUG)
    #     facade.set_console(level=logging.DEBUG, formatter=BACKGROUND_RENDER_CONSOLE_FORMATTER)
    #     self.logger = facade.get_logger()

    def start(self):
        """ 启动机器人 """
        return self.state.start(self)

    def stop(self):
        """ 停止机器人 """
        return self.state.stop(self)

    def launch(self):
        """
        启动机器人线程，机器人上下文为了能够以同步的方式执行discord机器人的异步方法，使用子线程+事件循环的
        形式运行机器人，并通过提交异步函数的形式操作机器人，此方法将启动一个子线程以运行机器人携程事件循环
        """
        return self.state.launch(self)

    def terminate(self):
        """ 停止机器人线程 """
        return self.state.terminate(self)

    @property
    def identify(self):
        return self.state.identify

    @property
    def state(self) -> BotState:
        return self._state

    @state.setter
    def state(self, state: BotState):
        """
        设置机器人自身状态，此方法仅仅变更状态，不应该调用此方法变更机器人的状态
        而是使用update_state
        """
        self._state = state

    def update_state(self, state: BotState):
        if self.state: self.state.do_fadeout(self)  # 状态切出
        self.state = state  # 状态切入
        if self.state: self.state.do_enter(self)

    def init_bot_event_listener(self, eventbus: ExecutorEventEmitter):
        """ 挂载机器人事件监听器，主要针对机器人相关事件进行监听，即BotEvent """
        pass

    def do_init_bot_event_listener(self, eventbus: ExecutorEventEmitter):
        """ 初始化机器人事件监听器，实际执行 """
        self.init_bot_event_listener(eventbus)

    def init_bot_instance(self):
        """ 初始化上下文的亚托莉对象 """
        bot = BotInstance(command_prefix=self.get_command_prefix(),
                          intents=self.get_intents())
        self.bot_instance = bot  # 此处应优先初始化字段，避免空指针
        self.do_init_bot_event_hook(bot)
        self.do_init_bot_command(bot)

    def init_bot_command(self, bot: BotInstance):
        """ 初始化机器人命令 """
        pass

    def init_bot_event_hook(self, bot: BotInstance):
        """ 初始化机器人生命周期事件监听器 """
        pass

    def do_init_bot_command(self, bot: BotInstance):
        @bot.command()
        async def add(ctx, left: int, right: int):
            await ctx.send(left + right)

        @bot.command()
        async def repeat(ctx, times: int, content='repeating...'):
            """Repeats a message multiple times."""
            for i in range(times):
                await ctx.send(content)

        self.init_bot_command(bot)

    def do_init_bot_event_hook(self, bot: BotInstance):
        @bot.event
        async def on_connect():
            """ 机器人成功建立的连接 """
            self.bot_eventbus.emit(BotEvent.CONNECT_SUCCESS)

        @bot.event
        async def on_disconnect():
            """ 机器人断开连接 """
            self.bot_eventbus.emit(BotEvent.DISCONNECT_SUCCESS)
        self.init_bot_event_hook(bot)

    # todo: 增加阻塞方法，支持以同步形式启动机器人上下文

    @abstractmethod
    def get_command_prefix(self) -> str:
        pass

    def get_intents(self) -> Intents:
        return Intents.all()
