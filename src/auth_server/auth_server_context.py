from flask_sqlalchemy import SQLAlchemy
from redis import Redis, StrictRedis

from utils.context import ApplicationContextV1, DefaultConfigKey, EnableSocketIO, EnableNacos, \
    EnableSwagger, EnableDatabase, EnableCache, SessionEnhance, EnableCors, SessionConfigKey


class AuthServerConfigKey(DefaultConfigKey):
    # yt-dlp配置
    YT_DLP_NAME = 'yt-dlp.name'
    # discord配置
    DISCORD_API_ENDPOINT = 'application.discord.api-endpoint'
    DISCORD_OAUTH_SCOPE = 'application.discord.oauth.scope'
    DISCORD_OAUTH_CLIENT_ID = 'application.discord.oauth.client-id'
    DISCORD_OAUTH_CLIENT_SECRET = 'application.discord.oauth.client-secret'
    DISCORD_OAUTH_REDIRECT_URI = 'application.discord.oauth.redirect-uri'
    # 网易云音乐api配置
    NETEASECLOUDMUSIC_API_URL = 'neteasecloudmusic-api.url'

@EnableNacos()  # 注册发现
@EnableSocketIO()  # 长连接
@EnableSwagger()  # 接口文档
@EnableDatabase()  # 数据库
@EnableCache()  # 缓存
@SessionEnhance()  # 会话增强
@EnableCors()  # 启用cors
class AuthServerContext(ApplicationContextV1):
    """ 用户接口服务 """
    db: SQLAlchemy
    redis: Redis  # redis客户端

    banner = """
        __  ___           _            __       _       ___         __  __  
       /  |/  /_  _______(_)________ _/ /______(_)     /   | __  __/ /_/ /_ 
      / /|_/ / / / / ___/ / ___/ __ `/ __/ ___/ /_____/ /| |/ / / / __/ __ \\
     / /  / / /_/ (__  ) / /__/ /_/ / /_/ /  / /_____/ ___ / /_/ / /_/ / / /
    /_/  /_/\__,_/____/_/\___/\__,_/\__/_/  /_/     /_/  |_\__,_/\__/_/ /_/ """

    def __init__(self):
        super().__init__('auth-server')  # 命名空间

    def pre_init(self):
        self.init_config_extension()  # 初始化配置拓展

    def post_init(self):
        self.init_models()  # 初始化数据库表
        # self.init_redis()  # 初始化redis客户端
        self.init_views()   # 初始化路由

        self.init_flask_lifecycle_event()

    def init_config_extension(self):
        """ 初始化配置拓展 """
        # discord相关配置
        self.config_schema['application']['schema']['discord'] = {
            'type': 'dict',
            'schema': {
                'api-endpoint': {'type': 'string', 'default': 'https://discord.com/api/v10'},
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
        }

        # 网易云服务配置
        self.config_schema['neteasecloudmusic-api'] = {
            'type': 'dict',
            'schema': {
                'url': {'type': 'string', 'default': 'http://127.0.0.1:3000'}
            }
        }

        # yt-dlp配置
        self.config_schema['yt-dlp'] = {
            'type': 'dict',
            'schema': {
                'name': {'type': 'string', 'default': 'musicatri'}
            }
        }

    def init_models(self):
        self.db.init_app(self.app)
        import auth_server.domain.models as models
        models.init(self.app)

    def init_views(self):
        """ 初始化路由 """
        from auth_server.views.static_blueprint import static_bp_v1
        from auth_server.views.system_blueprint import status_bp_v1
        from auth_server.views.auth_blueprint import auth_bp_v1
        from auth_server.views.user_blueprint import user_bp_v1

        self.app.register_blueprint(static_bp_v1)
        self.app.register_blueprint(status_bp_v1)
        self.app.register_blueprint(auth_bp_v1)
        self.app.register_blueprint(user_bp_v1)

        from auth_server.views.admin.user_blueprint import admin_user_bp_v1
        self.app.register_blueprint(admin_user_bp_v1)

    def init_redis(self):
        redis_host = self.config.get(SessionConfigKey.SESSION_REDIS_HOST)
        redis_port = self.config.get(SessionConfigKey.SESSION_REDIS_PORT)
        redis_db = self.config.get(SessionConfigKey.SESSION_REDIS_DATABASE)
        self.redis = StrictRedis(host=redis_host, port=redis_port, db=redis_db)

    def init_flask_lifecycle_event(self):
        """ 注册flask生命周期事件 """
        # @self.app.before_request
        # def print_session():
        #     from flask import request
        #     self.logger.info(f"session raw: {dict(self.session)}")
        #     self.logger.info(f'session id: {request.cookies.get("session")}')

context = AuthServerContext()
context.initialize()
