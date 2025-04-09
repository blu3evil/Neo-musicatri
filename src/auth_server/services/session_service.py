from flask import request, current_app
from auth_server.auth_server_context import context
from auth_server.services.cache_service import cache_service

from utils.context import SessionConfigKey
from common import Result

# redis = context.redis
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
    def register_user_session(user_id, user_token: dict):
        """ 注册用户会话 """
        session['discord_oauth_token'] = user_token
        session['user_id'] = user_id  # 存储user_id到session
        return Result(200)

    def upsert_user_session(self, user_id):
        # 建立用户id到session_id的映射，禁用过期
        result = cache_service.set_user_session_key(user_id, self._user_session_key())
        return result

    @staticmethod
    def unregister_user_session(user_id):
        """
        注销用户会话，通过cache_service建立的user_id到session_key的映射，获取Session_key，
        从而删除对应的session文件（filesystem-session场景下），或是直接删除redis key-value
        （redis存储场景下）
        """
        # todo: 补全针对文件模式下的session文件删除，实现注销会话
        # 实际上可以拓展更多存储场景，取决于flask-session
        _ = locale.get()

        result = cache_service.clear_user_session_key(user_id=user_id)  # 删除用户登录凭证
        if result.code != 200: return result

        # if session_type == 'redis':
        #     # 会话使用redis存储，通过cache读取对应的session_key进行删除
        #     result = cache_service.get_user_session_key(user_id)
        #     if result.code != 200: return result
        #
        #     user_session_key = result.data['user_session_key']
        #     redis.delete(user_session_key)  # 删除用户会话
        #
        #     return Result(200)

        return Result(200, message=_('unregister user session successfully'))

    @staticmethod
    def get_current_user_id():
        """ 返回当前用户的id """
        _ = locale.get()
        user_id = session.get('user_id')
        if user_id:
            return Result(200, data={'user_id': user_id})
        return Result(404, message=_('no user id was found'))

    @staticmethod
    def get_current_user_session_token():
        _ = locale.get()
        session_token = session.get('discord_oauth_token')
        if session_token:
            return Result(200, data={'session_token': session_token})
        return Result(404, message=_('no session token was found'))

session_service = SessionService()