"""
discord客户端
"""
from abc import abstractmethod

from modo.dto.discord_client_dto import DiscordOAuth2CredentialDTO, DiscordUserDTO
from utils.result import HttpResult
class DiscordClient:
    """ discord客户端接口 """
    @abstractmethod
    def fetch_oauth2_credential(self, code: str) -> HttpResult[DiscordOAuth2CredentialDTO]:
        """
        通过code获取discord access token
        参数说明:
          - code: 通过clientId请求discord认证接口获取的授权码
        """
        pass

    @abstractmethod
    def fetch_user(self, access_token: str) -> HttpResult[DiscordUserDTO]:
        """
        拉取用户信息，需要access token在申请时至少拥有identify权限

        响应码:
        - SUCCESS 20000 - 成功拉取用户信息
        - TOKEN_INVALID 40005 - access token无效
        - NETWORK_ERROR 40007 - 网络错误，通常由于代理引起
        - INTERNAL_SERVER_ERROR 50000 - 服务端未捕获错误
        """
        pass

    @abstractmethod
    def refresh_token(self, refresh_token: str) -> HttpResult[DiscordOAuth2CredentialDTO]:
        """
        使用用户的refresh token刷新用户的access token，此接口可在用户的access token过期时调用

        响应码:
        - SUCCESS 20000 - 成功成功刷新token信息
        - TOKEN_INVALID 40005 - access token无效
        - NETWORK_ERROR 40007 - 网络错误，通常由于代理引起
        - INTERNAL_SERVER_ERROR 50000 - 服务端未捕获错误
        """

