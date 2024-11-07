from __future__ import annotations

from abc import abstractmethod

from injector import Module, Binder, singleton

from repository.abs.discord_oauth2_session_mapper import DiscordOAuth2SessionMapper
from repository.abs.discord_user_mapper import DiscordUserMapper
from repository.abs.permission_mapper import PermissionMapper
from repository.abs.socketio_session_mapper import SocketIOSessionMapper
from repository.abs.user_permission_mapper import UserPermissionMapper
from repository.abs.user_session_mapper import UserSessionMapper
from repository.abs.transaction_manager import TransactionManager


class DatabaseClient(Module):
    """
    数据库连接客户端抽象工厂，实现之后返回对应的mapper实例，从而实现底层数据库的连接驱动切换
    """
    @abstractmethod
    def get_discord_user_mapper(self) -> DiscordUserMapper:
        """
        discord用户信息映射器工厂方法，构建discord用户信息库表映射对象，执行对discord用户信息库表的
        相关业务方法，musicatri使用discord用户信息直接作为项目的用户信息，因此该库表同时作为musicatri
        的用户信息库表
        """
        pass

    @abstractmethod
    def get_discord_oauth2_session_mapper(self) -> DiscordOAuth2SessionMapper:
        """
        discord oauth2认证会话信息映射器工厂方法，操作discord oauth2会话相关数据，存储discord oauth2会话认证凭据
        在用户完成discord oauth2授权流程之后此oauth2会话信息将会被存入此数据库表，同时作为musicatri的登入
        凭据，项目根据此库表数据构建一个基于musicatri项目的APP_SECRET_KEY的access token密钥，作为用户与musicatri
        的会话凭据
        """
        pass

    @abstractmethod
    def get_user_session_mapper(self) -> UserSessionMapper:
        """
        用户会话映射器工厂方法，即用户与musicatri站点之间的会话凭据，用户在完成discord oauth2授权之后将会为用户创建一份
        到musicatri的会话信息，从而避免用户需要频繁进行discord oauth2授权来使用musicatri
        """
        pass

    @abstractmethod
    def get_user_permission_mapper(self) -> UserPermissionMapper:
        """
        用户权限信息映射器工厂方法，此库表映射从用户id到权限id的关系，由于一个用户可以映射到多个权限等级，一个权限等级也可以
        映射到多个用户，因此设计了设个库表来处理多对多的映射关系，基于此库表来完成权限校验工作
        """
        pass

    @abstractmethod
    def get_permission_mapper(self) -> PermissionMapper:
        """
        权限信息详情映射器工厂方法，返回权限等级的定义详情，例如权限等级rank，以及权限描述信息，配合user_permission_mapper
        来完成完整的权限校验工作
        """
        pass

    @abstractmethod
    def get_socketio_session_mapper(self) -> SocketIOSessionMapper:
        """
        用户socketio会话连接映射器工厂方法，用户在完成登录之后会与站点建立socketio长连接，使用这个库表来维持用户的
        socketio会话信息，从而实现定向推送消息等功能
        """
        pass

    @abstractmethod
    def get_transaction_manager(self) -> TransactionManager:
        """
        事务管理器工厂方法，即平台事务管理器，平台事务管理器提供了统一的一组接口来操作数据库的事务，用于在出现异常时执行回滚，
        以及在事务正常进行之后执行提交
        """
        pass

    def configure(self, binder: Binder):
        """
        模块初始化方法，可以通过injector使用模块下载来将数据库客户端加载进入项目容器当中，从而避免手动注册数据库表映射器
        :param binder: 项目容器使用的绑定器
        """
        binder.bind(DiscordUserMapper, to=self.get_discord_user_mapper(), scope=singleton)  # discord用户信息库表
        binder.bind(DiscordOAuth2SessionMapper, to=self.get_discord_oauth2_session_mapper(), scope=singleton)  # discord oauth2会话信息库表
        binder.bind(UserSessionMapper, to=self.get_user_session_mapper(), scope=singleton)  # 用户会话信息库表
        binder.bind(UserPermissionMapper, to=self.get_user_permission_mapper(), scope=singleton)  # 用户权限信息映射库表
        binder.bind(PermissionMapper, to=self.get_permission_mapper(), scope=singleton)  # 权限库表
        binder.bind(SocketIOSessionMapper, to=self.get_socketio_session_mapper(), scope=singleton)  # socketio连接会话库表
        binder.bind(TransactionManager, to=self.get_transaction_manager(), scope=singleton)  # 平台事务管理器
