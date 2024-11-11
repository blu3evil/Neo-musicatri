from container.base_context import BaseContext

class ServiceContext(BaseContext):
    """ 业务层容器 """
    def setup(self):
        """  初始化容器 预加载所有可能用到的资源  """  # 改用懒加载
        # musicatri services
        from services.abs.atri_service import AtriService
        def atri_service_supplier() -> AtriService:
            from services.impl.atri_service_impl import AtriServiceImpl
            return AtriServiceImpl()
        self.lazy_register(AtriService, atri_service_supplier)

        # auth session
        from services.abs.auth_service import AuthService
        def oauth_service_supplier() -> AuthService:
            from services.impl.auth_service_impl import AuthServiceDiscordImpl
            return AuthServiceDiscordImpl()
        self.lazy_register(AuthService, oauth_service_supplier)

        # permission services
        from services.abs.permission_service import PermissionService
        def permission_service_supplier() -> PermissionService:
            from services.impl.permission_service_impl import PermissionServiceImpl
            return PermissionServiceImpl()
        self.lazy_register(PermissionService, permission_service_supplier)

        # discord oauth2 session services
        # from services.base_service.session_service import DiscordOAuth2SessionService
        # def discord_oauth2_session_supplier() -> DiscordOAuth2SessionService:
        #     from



services = ServiceContext()  # 业务层容器
