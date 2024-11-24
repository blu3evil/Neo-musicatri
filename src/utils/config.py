""" 更简洁的项目配置文件 """
import os

import yaml
from cerberus import Validator

# 配置参数校验
schema = {
    # 应用信息配置
    'environment': {'type': 'string', 'default': 'global'},
    'active-environment': {'type': 'string', 'default': 'global'},
    'application': {
        'type': 'dict',
        'schema': {
            # 是否开启dev模式
            'dev-mode': {'type': 'boolean', 'default': False},
            'debug-mode': {'type': 'boolean', 'default': False},
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
                            'file-directory': {'type': 'string', 'default': 'runtime/logs'},
                        }
                    },
                    'flask-logging': {
                        'type': 'dict',
                        'schema': {
                            'enable': {'type': 'boolean', 'default': True},
                        }
                    }
                }
            },
            # 网络配置
            'network': {
                'type': 'dict',
                'schema': {
                    'host': {'type': 'string', 'default': '127.0.0.1'},
                    'port': {'type': 'integer', 'default': 5000},
                    'public-url': {'type': 'string', 'default': 'http://127.0.0.1:5000'},
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
            'database': {
                'type': 'dict',
                'schema': {
                    'driver': {'type': 'string', 'default': 'mysql'},
                    'host': {'type': 'string', 'default': '127.0.0.1'},
                    'port': {'type': 'integer', 'default': 3306},
                    'username': {'type': 'string', 'default': 'root'},
                    'password': {'type': 'string', 'default': '1234'},
                    'database': {'type': 'string', 'default': 'musicatri'},
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
                            'file-directory': {'type': 'string', 'default': 'runtime/session'},
                        }
                    }
                }
            },
            'cache': {
                'type': 'dict',
                'schema': {
                    'type': {'type': 'string', 'default': 'filesystem'},
                    'timeout': {'type': 'integer', 'default': 60},  # 缓存过期时间，也是刷新缓存间隔
                    'key-prefix': {'type': 'string', 'default': 'cache:'},
                    'ignore-errors': {'type': 'boolean', 'default': False},  # 忽略缓存错误
                    'filesystem': {
                        'type': 'dict',
                        'schema': {
                            'file-threshold': {'type': 'integer', 'default': 5000},
                            'file-directory': {'type': 'string', 'default': 'runtime/cache'},
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
                    'api-endpoint': {'type': 'string', 'default': 'https://discord.com/api/v10'},
                    'bot': {
                        'type': 'dict',
                        'schema': {
                            'token': {'type': 'string', 'default': 'token'},
                        }
                    },
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
            'neteasecloudmusic-api': {
                'type': 'dict',
                'schema': {
                    'url': {'type': 'string', 'default': 'http://127.0.0.1:3000'},
                }
            },
        }
    },
}

from enum import Enum

class ConfigEnum(Enum):
    # 应用配置
    APP_DEV_MODE = 'application.dev-mode'
    APP_DEBUG_MODE = 'application.debug-mode'
    APP_INFO_NAME = 'application.information.name'
    APP_INFO_VERSION = 'application.information.version'
    APP_INFO_DESCRIPTION = 'application.information.description'
    APP_SECURITY_SECRET_KEY = 'application.security.secret-key'
    APP_SECURITY_OAUTH_INSECURE_TRANSPORT = 'application.security.oauth.insecure-transport'
    APP_SECURITY_OAUTH_RELAX_TOKEN_SCOPE = 'application.security.oauth.insecure-transport'
    APP_LOG_PRINT_BANNER = 'application.logging.print-banner'
    APP_LOG_DEFAULT_LOGGING_ENABLE = 'application.logging.default-logging.enable'
    APP_LOG_DEFAULT_LOGGING_LEVEL = 'application.logging.default-logging.level'
    APP_LOG_CONSOLE_LOGGING_ENABLE = 'application.logging.console-logging.enable'
    APP_LOG_CONSOLE_LOGGING_LEVEL = 'application.logging.console-logging.level'
    APP_LOG_LOGFILE_LOGGING_ENABLE = 'application.logging.logfile-logging.enable'
    APP_LOG_LOGFILE_LOGGING_LEVEL = 'application.logging.logfile-logging.level'
    APP_LOG_LOGFILE_LOGGING_EXTNAME = 'application.logging.logfile-logging.extname'
    APP_LOG_LOGFILE_LOGGING_FILE_DIRECTORY = 'application.logging.logfile-logging.file-directory'
    APP_LOG_FLASK_LOGGING_ENABLE = 'application.logging.flask-logging.enable'
    APP_NETWORK_HOST = 'application.network.host'
    APP_NETWORK_PORT = 'application.network.port'
    APP_NETWORK_PUBLIC_URL = 'application.network.public-url'
    APP_NETWORK_CORS_ALLOW_ORIGINS = 'application.network.cors.allow-origins'
    APP_NETWORK_CORS_ALLOW_HEADERS = 'application.network.cors.allow-headers'
    APP_NETWORK_CORS_ALLOW_METHODS = 'application.network.cors.allow-methods'
    APP_NETWORK_CORS_SUPPORTS_CREDENTIALS = 'application.network.cors.supports-credentials'

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
    DISCORD_API_ENDPOINT = 'services.discord.api-endpoint'
    DISCORD_BOT_TOKEN = 'services.discord.bot.token'
    DISCORD_OAUTH_CLIENT_ID = 'services.discord.oauth.client-id'
    DISCORD_OAUTH_CLIENT_SECRET = 'services.discord.oauth.client-secret'
    DISCORD_OAUTH_SCOPE = 'services.discord.oauth.scope'
    DISCORD_OAUTH_REDIRECT_URI = 'services.discord.oauth.redirect-uri'

    # 网易云音乐api配置
    NETEASECLOUDMUSIC_API_URL = 'services.neteasecloudmusic.url'

class ApplicationConfig:
    """
    项目配置类，通过Tag枚举类来更方便地获取项目配置
    """
    def __init__(self):
        self.configurations = {}  # 项目配置
        self.load_config()

    def _merge_dicts(self, old_dict, new_dict):
        """
        合并字典，使用new_dict当中的键值更新old_dict当中的键值，此方法为深度拷贝，拷贝过程中
        如果存在dict类型属性那么会执行递归拷贝
        """
        result = old_dict.copy()
        for key, value in new_dict.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                # 字典类型，执行递归拷贝
                result[key] = self._merge_dicts(result[key], value)
            elif value is not None:
                # 一般类型，仅仅当value存在时执行更新，这里需要确切判断不为none
                result[key] = value
        return result

    # noinspection PyShadowingNames
    def process_default_config(self, schema):
        """
        基于cerberus定义的表单验证规则生成一份仅仅具备配置结构的空白骨架，并通过随后的用户配置
        以及默认配置完成配置构建
        """
        default_config = self._do_process_default_config({}, schema)
        return default_config

    # noinspection PyShadowingNames
    def _do_process_default_config(self, default_config, schema):
        """ 实际执行构建基础配置 """
        for field, field_schema in schema.items():
            if field not in default_config:
                # 字段不存在
                if field_schema['type'] == 'dict' and 'schema' in field_schema:
                    # 字段类型为dict，直接将字段初始化为字典
                    # 同时通过递归来初始化字典
                    default_config[field] = {}

                    # 执行递归
                    self._do_process_default_config(default_config[field], field_schema['schema'])

                else:
                    # 将值赋值为空
                    if field == 'environment' and not default_config.get(field):
                        # 将环境值默认填充为global
                        default_config[field] = 'global'
                    elif field == 'active-environment' and not default_config.get(field):
                        # 默认激活环境为global
                        default_config[field] = 'global'

                    # 默认赋值为空
                    else: default_config[field] = None

        return default_config

    def load_config(self):
        """
        加载项目配置
        """
        root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        yaml_path = os.path.join(root_path, 'config.yaml')
        yml_path = os.path.join(root_path, 'config.yml')

        config_path = None

        if os.path.exists(yml_path): config_path = yml_path
        elif os.path.exists(yaml_path): config_path = yaml_path

        if config_path:
            # 配置路径存在，加载配置
            with open(config_path, 'r', encoding='utf-8') as file:
                origins = list(yaml.safe_load_all(file))
        else:
            # 配置路径不存在，使用空配置
            origins = {}

        self._do_load_config(origins)

    def _do_load_config(self, origins: dict):
        """
        基于路径加载配置文件
        :param origins: config.yml或config.yaml当中的配置项
        """
        if not origins:
            # origins 为空，直接将origins初始化为默认配置
            origins = self.process_default_config(schema)

        available_configs = {}  # 可用的配置字典

        # 遍历所有环境
        for origin in origins:
            # origins 非空，尝试加载配置

            # 构建一份默认配置骨架，插入用户配置
            default_config = self.process_default_config(schema)
            merged_config = self._merge_dicts(default_config, origin)

            # 获取当前配置环境名进行存储进入字典
            # 获取环境名
            environment_name = merged_config['environment']
            if not available_configs.get(environment_name):
                available_configs[environment_name] = merged_config
            else:
                # 若环境已经存在那么执行覆盖
                # 这能够避免一些同名环境被重复创建，因为这些同名配置最后将会被合并
                available_configs[environment_name] = self._merge_dicts(available_configs[environment_name], merged_config)

        try:
            global_config = available_configs['global']  # 获取全局环境
        except KeyError:
            # global环境未定义
            raise RuntimeError("'global' config not found")

        # 使用校验器补齐缺失参数
        v = Validator(schema, purge_unknown=True)

        if len(global_config) == 1:
            # 仅存在global一套配置，直接使用全局配置
            self.configurations = v.normalized(global_config)
            return

        # 存在多套配置文件，获取当前激活环境
        active_config_name = global_config['active-environment']

        try:
            active_config = available_configs[active_config_name]
        except KeyError:
            # 未找到指定环境
            raise RuntimeError(f"'{active_config_name}' config not found")


        # 将全局环境和激活环境合成，得到最终配置
        merged_config = self._merge_dicts(global_config, active_config)
        self.configurations = v.normalized(merged_config)

    from typing import Any
    def get(self, tag: ConfigEnum) -> Any:
        """
        通过Tag标签获取项目配置
        :param tag: 枚举类配置项
        :return: 项目配置信息
        """
        path = tag.value
        keys = path.split('.')
        value = self.configurations
        for key in keys:
            try:
                value = value[key]
            except KeyError:
                raise RuntimeError(f"{tag.name}({path}) not found '{key}'")
        return value

config = ApplicationConfig()


if __name__ == '__main__':
    print(config.configurations)


