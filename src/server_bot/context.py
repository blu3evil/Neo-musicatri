from __future__ import annotations
from utils.context import *

from server_bot.bot.atri.context import BotAtriContext
from utils.locale import FlaskLocaleFactory

@EnableNacos()  # 注册发现
@EnableSwagger()  # 接口文档
@EnableCors()  # 启用cors
@EnableI18N(factory_supplier=FlaskLocaleFactory)  # 启用本地化
class ServerBotContext(PluginSupportMixin, WebApplicationContext):
    """ 机器人服务，将机器人操作封装为API接口，提供HTTP调用的能力 """
    # 字体: https://toolinone.com/cn/text-ascii/ Slant
    banner = """
        __  _____  _______ _____________  __________  ____     ____  ____  ______
       /  |/  / / / / ___//  _/ ____/   |/_  __/ __ \/  _/    / __ )/ __ \/_  __/
      / /|_/ / / / /\__ \ / // /   / /| | / / / /_/ // /_____/ __  / / / / / /   
     / /  / / /_/ /___/ // // /___/ ___ |/ / / _, _// /_____/ /_/ / /_/ / / /    
    /_/  /_/\____//____/___/\____/_/  |_/_/ /_/ |_/___/    /_____/\____/ /_/     """

    atri_context: BotAtriContext  # 亚托莉上下文

    def __init__(self):
        super().__init__('server-bot')

    def _init_views(self):
        """ 蓝图初始化 """
        from views.atri_blueprint import atri_bp_v1
        self.app.register_blueprint(atri_bp_v1)

    def _init_atri(self):
        """ 初始化亚托莉上下文 """
        self.atri_context = BotAtriContext()
        self.atri_context.initialize()

    def post_init(self) -> InitHook:
        def hook_func():
            self._init_atri()
            self._init_views()
        return InitHook(hook_func)

context = ServerBotContext()
context.initialize()
