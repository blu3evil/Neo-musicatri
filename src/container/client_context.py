from container.base_context import BaseContext

class ClientContext(BaseContext):
    """ http客户端容器 """
    def setup(self):
        # discord客户端
        from client.discord_client import DiscordClient
        def discord_client_supplier():  # 懒加载实现
            from client.implement.discord_client_impl import DiscordClientImpl
            return DiscordClientImpl()
        self.lazy_register(DiscordClient, discord_client_supplier)


clients = ClientContext()  # 客户端容器
