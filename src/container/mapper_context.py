from container.base_context import BaseContext

class MapperContext(BaseContext):
    """ 映射器容器 """
    def setup(self):
        # todo: 根据配置逻辑修改使用的连接工厂实现
        # 目前默认使用mongodb连接工厂
        from repository.mongo.mongo_client import MongoClient
        client = MongoClient()

        # 注入mapper对象
        from repository.abs.socketio_session_mapper import SocketIOSessionMapper
        from repository.abs.permission_mapper import PermissionMapper
        from repository.abs.user_permission_mapper import UserPermissionMapper
        from repository.abs.user_session_mapper import UserSessionMapper
        from repository.abs.discord_oauth2_session_mapper import DiscordOAuth2SessionMapper
        from repository.abs.discord_user_mapper import DiscordUserMapper
        from repository.abs.transaction_manager import TransactionManager

        # 分布注入容器  采用懒加载
        # discord用户信息映射器
        self.lazy_register(DiscordUserMapper, lambda : client.get_discord_user_mapper())

        # discord oauth2认证信息映射器
        self.lazy_register(DiscordOAuth2SessionMapper, lambda : client.get_discord_oauth2_session_mapper())

        # 用户jwt认证信息映射器
        self.lazy_register(UserSessionMapper, lambda : client.get_user_session_mapper())

        # 用户权限等级映射器
        self.lazy_register(UserPermissionMapper, lambda : client.get_user_permission_mapper())

        # 权限等级详情映射器
        self.lazy_register(PermissionMapper, lambda : client.get_permission_mapper())

        # 用户socketio连接信息映射器
        self.lazy_register(SocketIOSessionMapper, lambda : client.get_socketio_session_mapper())

        # 平台事务管理器
        self.lazy_register(TransactionManager, lambda : client.get_transaction_manager())


mappers = MapperContext()  # 映射器容器