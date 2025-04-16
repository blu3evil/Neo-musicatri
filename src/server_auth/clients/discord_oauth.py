from authlib.oauth2.rfc6749 import InvalidGrantError
from requests import RequestException
from requests.exceptions import SSLError
from requests_oauthlib import OAuth2Session
from werkzeug.exceptions import InternalServerError, BadRequest

from requests.auth import HTTPBasicAuth

from server_auth.context import context, ServerAuthConfigKey

config = context.config

api_endpoint = config.get(ServerAuthConfigKey.DISCORD_API_ENDPOINT)
scope = config.get(ServerAuthConfigKey.DISCORD_OAUTH_SCOPE)
client_id = config.get(ServerAuthConfigKey.DISCORD_OAUTH_CLIENT_ID)
redirect_uri = config.get(ServerAuthConfigKey.DISCORD_OAUTH_REDIRECT_URI)
client_secret = config.get(ServerAuthConfigKey.DISCORD_OAUTH_CLIENT_SECRET)

def refresh_token(_refresh_token) -> dict:
    """
    刷新用户token
    :param _refresh_token: 用户刷新token
    :return:
    """
    oauth = OAuth2Session()
    token_url = f'{api_endpoint}/oauth2/token'
    try:
        new_token = oauth.refresh_token(
            token_url,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=_refresh_token
        )
        return new_token
    except RequestException as e:
        raise RuntimeError(e)


def fetch_token(code) -> dict:
    """
    拉取用户授权凭证信息
    :param code: 用户授权码
    :return:
    """
    try:
        oauth = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, scope=scope)
        token = oauth.fetch_token(
            token_url=f'{api_endpoint}/oauth2/token',
            authorization_response=f'{redirect_uri}?code={code}',
            client_secret=client_secret,
        )
        return token
    except RequestException as e:
        raise RuntimeError(e)


def fetch_user(access_token) -> dict:
    """
    拉取用户数据
    :param access_token:
    :return:
    """
    oauth = OAuth2Session(token={'access_token': access_token})
    try:
        response = oauth.get(f'{api_endpoint}/users/@me')  # 请求用户数据
    except InvalidGrantError:
        raise BadRequest  # 参数错误
    except SSLError:
        raise InternalServerError  # SSL错误

    if not response.status_code == 200:
        raise RuntimeError(response.status_code)
    return response.json()


def get_authorize_url() -> str:
    """ 构建认证链接 """
    authorize_url = f'https://discord.com/api/oauth2/authorize?response_type=code&scope={scope}&client_id={client_id}&redirect_uri={redirect_uri}'
    return authorize_url


def revoke_access_token(access_token):
    """ 撤销访问令牌 """
    oauth = OAuth2Session()
    data = {
        'token': access_token,
        'token_type_hint': 'access_token',
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = oauth.post(f'{api_endpoint}/oauth2/token/revoke',
                          data=data,
                          headers=headers,
                          auth = HTTPBasicAuth(client_id, client_secret))

    if not response.status_code == 200:
        raise RuntimeError(response.status_code)
