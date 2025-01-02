from utils.context import ApplicationContextV1, DefaultConfigKey

class ApiServerConfigKey(DefaultConfigKey):
    # yt-dlp配置
    YT_DLP_NAME = 'yt-dlp.name'
    # discord配置
    DISCORD_API_ENDPOINT = 'discord.api_server-endpoint'
    DISCORD_OAUTH_SCOPE = 'discord.oauth.scope'
    DISCORD_OAUTH_CLIENT_ID = 'discord.oauth.client-id'
    DISCORD_OAUTH_CLIENT_SECRET = 'discord.oauth.client-secret'
    DISCORD_OAUTH_REDIRECT_URI = 'discord.oauth.redirect-uri'
    # 网易云音乐api配置
    NETEASECLOUDMUSIC_API_URL = 'neteasecloudmusic-api.url'

class ApiServerContext(ApplicationContextV1):
    """ 用户接口服务 """
    banner = """
    ______  ___                _____                _____         _____ 
    ___   |/  /____  _____________(_)_____________ ___  /____________(_)
    __  /|_/ / _  / / /__  ___/__  / _  ___/_  __ `/_  __/__  ___/__  / 
    _  /  / /  / /_/ / _(__  ) _  /  / /__  / /_/ / / /_  _  /    _  /  
    /_/  /_/   \__,_/  /____/  /_/   \___/  \__,_/  \__/  /_/     /_/   """

    def __init__(self):
        super().__init__('api-server')  # 命名空间

    def pre_init(self):
        self.init_config_extension()  # 初始化配置拓展

    def post_init(self):
        self.init_models()  # 初始化数据库表
        self.init_views()   # 初始化路由

    def init_config_extension(self):
        """ 初始化配置拓展 """
        # discord相关配置
        self.config_schema['discord'] = {
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
        import api_server.domain.models as models
        models.init(self.app)

    def init_views(self):
        """ 初始化路由 """
        from views.static_blueprint import static_bp_v1
        from views.system_blueprint import status_bp_v1
        from views.auth_blueprint import auth_bp_v1
        from views.user_blueprint import user_bp_v1

        self.app.register_blueprint(static_bp_v1)
        self.app.register_blueprint(status_bp_v1)
        self.app.register_blueprint(auth_bp_v1)
        self.app.register_blueprint(user_bp_v1)

context = ApiServerContext()
context.initialize()
context.init_socketio()
