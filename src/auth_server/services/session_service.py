from flask import request, current_app
from typing_extensions import deprecated

from auth_server.context import context
from auth_server.services.cache_service import cache_service

from common.utils.context import SessionConfigKey
from common.domain.models import Result

# redis = auth_client.py.redis
session = context.session
config = context.config
locale = context.locale

session_prefix = config.get(SessionConfigKey.SESSION_KEY_PREFIX)  # 会话前缀
session_type = config.get(SessionConfigKey.SESSION_TYPE)  # 会话类型

class SessionService:
    """ 用户会话服务 """
    @staticmethod
    def _user_session_key():
        """ 存储用户会话时的键名 """
        with current_app.app_context():
            session_cookie_name = current_app.config.get('SESSION_COOKIE_NAME', "session")  # 存储在浏览器端的cookie名
            user_session_id = request.cookies.get(session_cookie_name)
            return f'{session_prefix}{user_session_id}'

    @staticmethod
    # @deprecated("token store in cache rather than session")
    def register_user_session(user_id):
        """ 注册用户会话 """
        # session['discord_oauth_token'] = user_token  # token写入缓存而不是session
        session['user_id'] = user_id  # 存储user_id到session
        return Result(200)

    def upsert_user_session(self, user_id):
        """ 使用缓存建立user_id到user_session_key的映射，实现手动维护session """
        # 建立用户id到session_id的映射，禁用过期
        result = cache_service.set_user_session_key(user_id, self._user_session_key())
        return result

    @staticmethod
    def get_current_user_id():
        """ 返回当前用户的id """
        _ = locale.get()
        user_id = session.get('user_id')
        if user_id:
            return Result(200, data={'user_id': user_id})
        return Result(404, message=_('no user id was found'))

    @staticmethod
    @deprecated("token store in cache rather than session")
    def get_current_user_session_token():
        _ = locale.get()
        session_token = session.get('discord_oauth_token')
        if session_token:
            return Result(200, data={'session_token': session_token})
        return Result(404, message=_('no session token was found'))

session_service = SessionService()