from __future__ import annotations

from abc import abstractmethod

from pattern.singleton import BaseSingleton
from repository.transaction_manager import TransactionManager
from repository.mapper.permission_mapper import PermissionMapper, UserPermissionMapper
from repository.mapper.session_mapper import UserSessionMapper, SocketIOSessionMapper, DiscordOAuth2SessionMapper
from repository.mapper.profile_mapper import DiscordUserMapper


class DatabaseClient(BaseSingleton):
    """
    数据库连接客户端抽象工厂，实现之后返回对应的mapper实例，从而实现底层数据库的连接驱动切换
    """
    @abstractmethod
    def get_discord_user_mapper(self) -> DiscordUserMapper:
        """ 返回discord用户信息映射器 """
        pass

    @abstractmethod
    def get_discord_oauth_session_mapper(self) -> DiscordOAuth2SessionMapper:
        """ 获取discord oauth认证会话信息映射器 """
        pass

    @abstractmethod
    def get_jwt_session_mapper(self) -> UserSessionMapper:
        """ 获取jwt会话映射器 """
        pass

    @abstractmethod
    def get_user_permission_mapper(self) -> UserPermissionMapper:
        """ 获取用户权限信息映射器 """
        pass

    @abstractmethod
    def get_permission_mapper(self) -> PermissionMapper:
        """ 获取权限信息详情映射器 """
        pass

    @abstractmethod
    def get_user_socketio_session_mapper(self) -> SocketIOSessionMapper:
        """ 获取用户websocket连接信息表 """
        pass

    @abstractmethod
    def get_transaction_manager(self) -> TransactionManager:
        """ 获取事务管理器 """
        pass
