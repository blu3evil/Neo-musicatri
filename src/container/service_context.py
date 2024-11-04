from container.base_context import BaseContext

class ServiceContext(BaseContext):
    """ 业务层容器 """
    def setup(self):
        """  初始化容器 预加载所有可能用到的资源  """  # 改用懒加载

        # 上层service
        # system service
        from service.upper_service.system_service import SystemService  # 懒加载
        def system_service_supplier() -> SystemService:
            from service.upper_service.implement.system_service_impl import SystemServiceImpl
            return SystemServiceImpl()
        self.lazy_register(SystemService, system_service_supplier)

        # musicatri service
        from service.upper_service.atri_service import AtriService
        def atri_service_supplier() -> AtriService:
            from service.upper_service.implement.atri_service_impl import AtriServiceImpl
            return AtriServiceImpl()
        self.lazy_register(AtriService, atri_service_supplier)

        # auth session
        from service.upper_service.auth_service import AuthService
        def oauth_service_supplier() -> AuthService:
            from service.upper_service.implement.auth_service_impl import AuthServiceImpl
            return AuthServiceImpl()
        self.lazy_register(AuthService, oauth_service_supplier)

        # permission service
        from service.base_service.permission_service import PermissionService
        def permission_service_supplier() -> PermissionService:
            from service.base_service.implement.permission_service_impl import PermissionServiceImpl
            return PermissionServiceImpl()
        self.lazy_register(PermissionService, permission_service_supplier)

        # discord oauth2 session service
        # from service.base_service.session_service import DiscordOAuth2SessionService
        # def discord_oauth2_session_supplier() -> DiscordOAuth2SessionService:
        #     from



services = ServiceContext()  # 业务层容器
