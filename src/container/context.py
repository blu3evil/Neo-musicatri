from injector import Module, provider, singleton

from repository.abs.user_session_mapper import UserSessionMapper
from service.abs.auth_service import AuthService
from service.abs.system_service import SystemService


class ApplicationContext(Module):
    @provider
    @singleton
    def system_service_provider(self) -> SystemService:
        """ 系统业务 """
        from service.impl.system_service_impl import SystemServiceImpl
        return SystemServiceImpl()

    @provider
    @singleton
    def auth_service_provider(self, user_session_mapper: UserSessionMapper) -> AuthService:
        """ 认证业务 """
        from service.impl.auth_service_impl import AuthServiceDiscordImpl
        return AuthServiceDiscordImpl(user_session_mapper)

    def configure(self, binder):
        """
        数据库客户端，未来可在这里替换数据库实现
        :param binder: 绑定器
        """
        from repository.mongo import MongoClient
        binder.install(MongoClient())


