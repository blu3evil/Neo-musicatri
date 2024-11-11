import requests
from requests import HTTPError
from typing_extensions import override

from client.discord_client import DiscordClient
from decorator import fallback
from modo.base_domain import BaseDomain
from modo.dto.discord_client_dto import DiscordOAuth2CredentialDTO, DiscordUserDTO
from utils import HttpResult, HttpCode, default_locale as _, default_config, DefaultConfigTag


class DiscordClientImpl(DiscordClient):
    @override
    @fallback(lambda error: HttpResult.error(HttpCode.NETWORK_ERROR, str(error)),HTTPError)  # http异常
    @fallback(lambda error: HttpResult.error(HttpCode.INTERNAL_SERVER_ERROR, str(error)),Exception)  # 一般异常
    def refresh_token(self, refresh_token: str) -> HttpResult[DiscordOAuth2CredentialDTO]:
        """ 刷新用户access token """
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        client_id = default_config.get(DefaultConfigTag.DISCORD_CLIENT_ID)
        client_secret = default_config.get(DefaultConfigTag.DISCORD_CLIENT_SECRET)
        # discord api端点
        discord_api_endpoint = default_config.get(DefaultConfigTag.DISCORD_API_ENDPOINT)
        # 请求刷新access token
        res = requests.post(f'{discord_api_endpoint}/oauth2/token', data=data, headers=headers, auth=(client_id, client_secret))
        res.raise_for_status()

        if res.status_code == 200:
            # access token刷新成功，# 构建dto
            dto = DiscordOAuth2CredentialDTO()
            BaseDomain.copy_properties(res.json(), dto)
            return HttpResult.success(HttpCode.SUCCESS, _('successfully refresh token'), dto)
        elif res.status_code == 401:
            # refresh token无效
            return HttpResult.error(HttpCode.TOKEN_INVALID, _('invalid refresh token'))
        else:
            # 未知异常
            return HttpResult.error(HttpCode.INTERNAL_SERVER_ERROR, HttpCode.INTERNAL_SERVER_ERROR.describe)


    @override
    @fallback(lambda error: HttpResult.error(HttpCode.NETWORK_ERROR, str(error)), HTTPError)  # http异常
    @fallback(lambda error: HttpResult.error(HttpCode.INTERNAL_SERVER_ERROR, str(error)), Exception)  # 一般异常
    def fetch_user(self, access_token: str) -> HttpResult[DiscordUserDTO]:
        """
        SUCCESS 20000 - 成功拉取用户信息
        TOKEN_INVALID 40005 - access token无效
        NETWORK_ERROR 40007 - 网络错误，通常由于代理引起
        INTERNAL_SERVER_ERROR 50000 - 服务端错误
        """
        headers = { 'Authorization': f'Bearer {access_token}' }
        discord_api_endpoint = default_config.get(DefaultConfigTag.DISCORD_API_ENDPOINT)
        response = requests.get(f'{discord_api_endpoint}/users/@me', headers=headers)

        response.raise_for_status()  # 抛出异常

        if response.status_code == 200:
            # 请求正常，正常响应用户信息
            dto = DiscordUserDTO()
            BaseDomain.copy_properties(response.json(), dto)
            return HttpResult.success(HttpCode.SUCCESS, _("successfully fetch user"), data=dto)
        elif response.status_code == 401:
            # token失效
            return HttpResult.error(HttpCode.TOKEN_INVALID, _('invalid access token'))
        else:
            # 未知异常
            return HttpResult.error(HttpCode.INTERNAL_SERVER_ERROR, HttpCode.INTERNAL_SERVER_ERROR.describe)


    @override
    @fallback(lambda error: HttpResult.error(HttpCode.CLIENT_ERROR, str(error)), HTTPError)  # http异常
    @fallback(lambda error: HttpResult.error(HttpCode.INTERNAL_SERVER_ERROR, str(error)), Exception)  # 一般异常
    def fetch_oauth2_credential(self, code: str) -> HttpResult[DiscordOAuth2CredentialDTO]:
        if not code:  # 请求参数不包含code
            result = HttpResult.error(HttpCode.INVALID_REQUEST_PARAMS, _("cannot acquire token without code"))
            return result

        # discord callback重定向uri
        redirect_uri = f'{default_config.get(DefaultConfigTag.PUBLIC_URL)}/api/oauth2/discord/callback'
        # discord oauth2认证client id
        client_id = default_config.get(DefaultConfigTag.DISCORD_CLIENT_ID)
        # discord oauth2认证client secret
        client_secret = default_config.get(DefaultConfigTag.DISCORD_CLIENT_SECRET)
        # discord oauth2认证末端节点，用于通过code请求token
        discord_api_endpoint = default_config.get(DefaultConfigTag.DISCORD_API_ENDPOINT)

        data = {  # 请求体
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }

        headers = {  # 请求头
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # 通过获取的有效参数请求token
        res = requests.post(f'{discord_api_endpoint}/oauth2/token',
                            data=data,
                            headers=headers,
                            auth=(client_id, client_secret))
        res.raise_for_status()  # 如果异常存在那么抛出异常

        if res.status_code == 200:
            # 请求成功
            dto = DiscordOAuth2CredentialDTO()
            BaseDomain.copy_properties(res.json(), dto)
            return HttpResult.success(HttpCode.SUCCESS, _("successfully acquire token"), data=dto)
        else:
            return HttpResult.error(HttpCode.INTERNAL_SERVER_ERROR, _("failed in fetching oauth2 credential"))