from datetime import datetime
from functools import wraps

from flask import session, abort
from flask_caching import Cache
from requests import RequestException
from requests_oauthlib import OAuth2Session

from utils.configs import config, ConfigEnum
client_id = config.get(ConfigEnum.DISCORD_OAUTH_CLIENT_ID)
client_secret = config.get(ConfigEnum.DISCORD_OAUTH_CLIENT_SECRET)
discord_api_endpoint = config.get(ConfigEnum.DISCORD_API_ENDPOINT)

class Auth:
    @staticmethod
    def validate_login() -> bool:
        session_token = session.get('discord_oauth_token', {})
        if not session_token:
            return False  # 无状态视为过期

        expires_at = session_token.get('expires_at')
        current_time = int(datetime.now().timestamp())
        if expires_at < current_time:
            # 此时已经超过过期时间，会话过期，执行刷新token
            oauth = OAuth2Session()
            refresh_token = session_token.get('refresh_token')
            token_url = f'{discord_api_endpoint}/oauth2/token'
            try:
                new_token = oauth.refresh_token(
                    token_url,
                    client_id=client_id,
                    client_secret=client_secret,
                    refresh_token=refresh_token
                )
                # 将新的token写入session
                session['discord_oauth_token'] = new_token
            except RequestException as ex:
                # refresh token过期或者无效
                return False
        return True  # 会话有效，正常执行

    @staticmethod
    def login_required(func):
        """ 基于session的登陆状态检查 """
        @wraps(func)
        def decorated(*args, **kwargs):
            if not auth.validate_login(): abort(401)
            return func(*args, **kwargs)  # 会话有效，正常执行
        return decorated

def init(app):
    cache.init_app(app)

auth = Auth()
cache = Cache()

