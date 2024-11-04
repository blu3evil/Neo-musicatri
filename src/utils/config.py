"""
项目配置文件加载工具类
"""

from utils.toolkit import BaseConfigTag, BaseConfig


# 验证器文档: https://docs.python-cerberus.org/validation-rules.html

class DefaultConfigTag(BaseConfigTag):
    """
    项目配置标签，通过使用这个枚举类来获取配置项
    如果需要定义配置项那么在这里添加，定义配置项以及配置项的默认值
    """
    # Musicatri配置项
    DEV_MODE = {  # 开发者模式
        'default': False,
        'type': 'boolean',
        'required': True,
    }

    PRINT_BANNER = {
        'default': True,
        'type': 'boolean',
        'required': True,
    }

    NETEASECLOUDMUSICAPI_URL = {  # 网易云音乐api后端url
        'default': "http://127.0.0.1:3000",
        'type': 'string',
        'regex': r'^(http://|https://)[a-zA-Z0-9._-]+(:[0-9]+)?(/.*)?$',
        'required': True,
    }

    DATABASE_URL = {  # 数据库资源路径
        'default': "mongodb://127.0.0.1:27017/musicatri",
        'type': 'string',
        'required': True,
    }

    MONGODB_URL = {  # mongodb数据库url(已经弃用)
        'default': "mongodb://127.0.0.1:3000",
        'type': 'string',
        'regex': "^(mongodb://)[a-zA-Z0-9._-]+(:[0-9]+)?(/.*)?$",
        'required': True,
        'deprecated': True
    }

    SERVER_PORT = {  # Musicatri后端服务端口号
        'default': 5000,
        'type': 'integer',
        'min': 0,
        'max': 65536,
    }

    SERVER_HOST = {  # Musicatri后端绑定ip
        'default': "127.0.0.1",
        'type': 'string',
        'required': True,
        'regex': r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
    }

    YOUTUBEDL_PROXY = {  # youtube-dl代理地址
        'default': "",
        'type': 'string'
    }

    PUBLIC_URL = {  # 公开路径，通常是前端的路径，后端需要用于oauth认证回调
        'type': 'string',
        'default': "http://127.0.0.1:5173",
        'regex': r'^(http://|https://)[a-zA-Z0-9._-]+(:[0-9]+)?(/.*)?$',
        'required': True,
    }

    APP_SECRET_KEY = {  # 应用密匙
        'type': 'string',
        'required': True,
        'sensitive': True,
        'default': "musicatri"
    }

    ACCESS_TOKEN_EXPIRES = {  # jwt过期时间，单位为秒
        'type': 'integer',
        'required': True,
        'min': 3600,  # 最短为5分钟
        'max': 86400,  # 最长为24小时
        'default': 3600  # 默认为1小时
    }

    JWT_REFRESH_TOKEN_EXPIRES = {  # refresh_token过期时间，单位为秒
        'type': 'integer',
        'required': True,
        'min': 86400,  # refresh token有效期最短时间为24小时
        'max': 2592000,  # 最长有效时间为1个月
        'default': 2592000,  # 默认有效时长为1个月
        'deprecated': True
    }

    DEFAULT_LOG_LEVEL = {  # 默认日志输出等级
        'type': 'string',
        'allowed': ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'FATAL', 'NOTSET', 'WARN'],
        'default': 'DEBUG',
        'required': True
    }
    CONSOLE_LOG_LEVEL = {  # 控制台日志等级
        'type': 'string',
        'allowed': ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'FATAL', 'NOTSET', 'WARN'],
        'default': 'INFO',
        'required': True
    }
    LOGFILE_LOG_LEVEL = {  # log文件日志等级
        'type': 'string',
        'allowed': ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'FATAL', 'NOTSET', 'WARN'],
        'default': 'DEBUG',
        'required': True
    }
    # discord配置项
    DISCORD_BOT_COMMAND_PREFIX = {  # 机器人命令前缀
        'default': "musicatri",
        'type': 'string',
        'required': True,
    }
    DISCORD_REDIRECT_URI = {  # OAuth2重定向认证地址
        'default': "http://127.0.0.1:3000/api/discord/oauth2",
        'type': 'string',
        'required': True,
        'regex': r'^(http://|https://)[a-zA-Z0-9._-]+(:[0-9]+)?(/.*)?$',
        'deprecated': True
    }
    DISCORD_API_ENDPOINT = {  # discord api版本路径
        'default': 'https://discord.com/api/v10',
        'type': 'string',
        'required': True,
        'regex': r'^(https://)[a-zA-Z0-9._-]+(:[0-9]+)?(/.*)?$',
    }
    DISCORD_CLIENT_ID = {  # discord客户端id
        'type': 'string',
        'required': True,
        'sensitive': True,
        'default': "discord_client_id",
    }
    DISCORD_CLIENT_SECRET = {  # discord客户端密匙
        'type': 'string',
        'required': True,
        'sensitive': True,
        'default': "discord_client_secret",
    }
    DISCORD_BOT_TOKEN = {  # discord机器人token
        'type': 'string',
        'required': True,
        'sensitive': True,
        'default': "discord_bot_token",
    }
    # todo: 更好的Banner显示
    DISCORD_BOT_BANNER = {  # discord机器人旗帜栏显示
        'type': 'string',
        'required': True,
        'default': "主人的命令|| <command_prefix> play<歌曲>||支持网易云，哔哩哔哩，youtube，ニコニコ"
    }
    DISCORD_BOT_ACTIVITY = {
        'type': 'integer',
        'required': True,
        'allowed': [-1, 0, 1, 2, 3, 4, 5],
        'default': 2,
    }
    # -1 : unknown
    # 0 : playing
    # 1 : streaming
    # 2 : listening
    # 3 : watching
    # 4 : custom
    # 5 : competing


class DefaultConfig(BaseConfig):
    """
    项目配置类，默认优先加载.env配置文件，如果.env文件配置项缺失，
    那么使用config.json配置文件，最后使用默认配置项
    """

    def __init__(self):
        # 采用默认日志实现
        super(DefaultConfig, self).__init__(DefaultConfigTag)
        self.load_default()  # 加载默认配置

        from utils.toolkit import ResourceUtils
        config_path = ResourceUtils.get_root_resource("config.json")
        if config_path:  self.load_jsonfile(config_path)  # 加载config.json配置

        self.load_env()  # 加载环境配置
        self.__apply_logger_config()  # 将配置应用到日志

    def __apply_logger_config(self):
        default_level = self.configurations.get(DefaultConfigTag.DEFAULT_LOG_LEVEL)
        console_level = self.configurations.get(DefaultConfigTag.CONSOLE_LOG_LEVEL)
        logfile_level = self.configurations.get(DefaultConfigTag.LOGFILE_LOG_LEVEL)
        from utils.logger import facade
        facade.set_default_level(default_level)
        facade.set_console_level(console_level)
        facade.set_logfile_level(logfile_level)


default_config = DefaultConfig()
