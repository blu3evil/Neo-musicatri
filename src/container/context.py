from injector import Module, provider, singleton

from services.abs.auth_service import AuthService


class ApplicationContext(Module):

    @provider
    @singleton
    def auth_service_provider(self) -> AuthService:
        """ 认证业务 """
        from services.impl.auth_service_impl import AuthServiceDiscordImpl
        return AuthServiceDiscordImpl()

    def configure(self, binder):
        """
        数据库客户端，未来可在这里替换数据库实现
        :param binder: 绑定器
        """
        from repository.mongo import MongoClient
        binder.install(MongoClient())


