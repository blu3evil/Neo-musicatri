from nacos import NacosClient

class AuthClient:
    """ 认证服务客户端 """
    nacos_client: NacosClient  # 服务发现

    def __init__(self, nacos_client):
        self.nacos_client = nacos_client

    def
