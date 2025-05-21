from redis import Redis, StrictRedis

from common.utils.locale import FlaskLocaleFactory
from common.utils.context import *
from common.aop.api_aspect import ApiAspect

class ServerAuthConfigKey:
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

@EnableNacosRegister()  # 注册注册
@EnableSocketIO()  # 长连接
@EnableSwagger()  # 接口文档
@EnableDatabase()  # 数据库
@EnableCache()  # 缓存
@SessionEnhance()  # 会话增强
@EnableCors()  # 启用cors
@EnableGunicorn()  # 启用gunicorn
@EnableApiAspect()  # 启用切面编程
@EnableJWT()  # 启用jwt
@EnableI18N(factory_supplier=FlaskLocaleFactory)  # 启用本地化
class AuthServerContext(PluginSupportMixin, WebApplicationContext):
    """ 用户接口服务 """
    db: SQLAlchemy
    redis: Redis  # redis客户端
    aspect: ApiAspect  # api切面

    from flask_jwt_extended import JWTManager
    jwt: JWTManager

    banner = """
        __  ___           _            __       _       ___         __  __  
       /  |/  /_  _______(_)________ _/ /______(_)     /   | __  __/ /_/ /_ 
      / /|_/ / / / / ___/ / ___/ __ `/ __/ ___/ /_____/ /| |/ / / / __/ __ \\
     / /  / / /_/ (__  ) / /__/ /_/ / /_/ /  / /_____/ ___ / /_/ / /_/ / / /
    /_/  /_/\__,_/____/_/\___/\__,_/\__/_/  /_/     /_/  |_\__,_/\__/_/ /_/ """

    def __init__(self):
        super().__init__('auth-server')  # 命名空间

    def pre_init(self) -> InitHook:
        def hook_func():
            """ 初始化配置拓展 """
            # discord相关配置
            self.config_schema_builder.set_at_path('application.discord', {
                'type': 'dict',
                'schema': {
                    'api-endpoint': {'type': 'string', 'default': 'https://discord.com/api/v10'},
                    'oauth': {
                        'type': 'dict',
                        'schema': {
                            'client-id': {'type': 'string', 'default': 'client-id'},
                            'client-secret': {'type': 'string', 'default': 'client-secret'},
                            'redirect-uri': {'type': 'string',
                                             'default': "http://localhost:5173/api/v1/auth/discord/authorized"},
                            'scope': {'type': 'string', 'default': 'identify guilds guilds.join'}
                        }
                    }
                }
            })
        return InitHook(hook_func)

    def post_init(self) -> InitHook:
        def hook_func():
            self._init_models()  # 初始化数据库表
            # self.init_redis()  # 初始化redis客户端
            self._init_views()  # 初始化路由
            self._init_jwt()
        return InitHook(hook_func)

    def _init_models(self):
        self.db.init_app(self.app)
        import auth_server.domain.models as models
        models.init(self.app)

    def _init_views(self):
        """ 初始化路由 """
        from auth_server.views.static_blueprint import static_bp_v1
        from auth_server.views.system_blueprint import status_bp_v1
        from auth_server.views.auth_blueprint import user_auth_bp_v1, user_auth_bp_v2, service_auth_bp_v2
        from auth_server.views.user_blueprint import user_bp_v1
        from auth_server.views.service.user_blueprint import service_user_bp_v1

        self.app.register_blueprint(static_bp_v1)
        self.app.register_blueprint(status_bp_v1)
        self.app.register_blueprint(user_auth_bp_v1)
        self.app.register_blueprint(user_auth_bp_v2)  # 用户认证路由v2
        self.app.register_blueprint(service_auth_bp_v2)  # 服务认证路由v2
        self.app.register_blueprint(user_bp_v1)
        self.app.register_blueprint(service_user_bp_v1)  # 服务-用户路由v1

        from auth_server.views.admin.user_blueprint import admin_user_bp_v1
        self.app.register_blueprint(admin_user_bp_v1)

    def _init_redis(self):
        redis_host = self.config.get(SessionConfigKey.SESSION_REDIS_HOST)
        redis_port = self.config.get(SessionConfigKey.SESSION_REDIS_PORT)
        redis_db = self.config.get(SessionConfigKey.SESSION_REDIS_DATABASE)
        self.redis = StrictRedis(host=redis_host, port=redis_port, db=redis_db)

    def _init_jwt(self):
        """ 注册flask生命周期事件 """
        from auth_server.services.cache_service import cache_service
        @self.jwt.token_in_blocklist_loader
        def validate_token(jwt_header, jwt_payload) -> bool:
            jti = jwt_payload['jti']
            return cache_service.is_token_revoked(jti)  # 通过缓存检查token是否已经被撤销

    def enable_boot_logger(self) -> bool:
        return False

context = AuthServerContext()
context.initialize()
