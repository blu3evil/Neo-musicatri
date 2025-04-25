import math

from common.utils.context import CacheConfigKey

from auth_server.context import context
from common.domain.models import Result

# redis = context.py.redis  # redis客户端
config = context.config  # 配置
cache = context.cache
locale = context.locale

cache_timeout = config.get(CacheConfigKey.CACHE_TIMEOUT)

class CacheService:
    """ 缓存服务 """
    @staticmethod
    def _user_info_ck(user_id: str):
        """ 用户数据缓存键名 """
        return f'users:{user_id}:info'

    @staticmethod
    def _user_roles_ck(user_id: str):
        """ 用户权限缓存键名 """
        return f'users:{user_id}:roles'

    @staticmethod
    def _user_session_key_ck(user_id: str):
        """ 用户id到session_key键名，用于建立用户id到session的映射 """
        return f'users:{user_id}:session'

    @staticmethod
    def _discord_oauth_token_ck(user_id: str):
        """ 用户discord oauth2认证令牌缓存键名 """
        return f'users:{user_id}:discord_oauth_token'

    @staticmethod
    def _revoked_token_ck(jti: str):
        """ 被吊销的token缓存键名，记录被吊销的 """
        return f'revoked:{jti}'

    def set_user_info(self, user_id, user_info: dict):
        """ 建立用户数据信息缓存 """
        cache_key = self._user_info_ck(user_id)
        self._set_cache(cache_key, user_info)  # 将用户数据写入缓存
        return Result(200)

    def set_discord_oauth_token(self, user_id, user_token: dict):
        """ 建立用户discord oauth2凭证缓存 """
        cache_key = self._discord_oauth_token_ck(user_id)

        expires_at = user_token.get('expires_at')
        self._set_cache(cache_key, user_token, timeout=expires_at)

        return Result(200)

    def get_discord_oauth_token(self, user_id):
        """ 获取用户discord oauth2凭证缓存 """
        cache_key = self._discord_oauth_token_ck(user_id)
        user_token = cache.get(cache_key)
        if user_token is None:
            return Result(404)
        return Result(200, data=user_token)

    def get_user_info(self, user_id):
        """ 获取用户信息缓存 """
        _ = locale.get()
        cache_key = self._user_info_ck(user_id)
        user_info = self._get_cache(cache_key)

        if user_info is None:
            return Result(404)  # 缓存未找到用户数据
        return Result(200, data=user_info, message=_('hit cache'))

    def set_user_roles(self, user_id, role_names: list):
        """ 建立用户权限信息缓存 """
        _ = locale.get()
        cache_key = self._user_roles_ck(user_id)
        self._set_cache(cache_key, role_names)
        return Result(200, _('successfully set user role into cache'))

    def get_user_roles(self, user_id):
        """ 获取用户权限缓存 """
        _ = locale.get()
        cache_key = self._user_roles_ck(user_id)
        user_roles = self._get_cache(cache_key)

        if user_roles: return Result(200, _('hit cache'), user_roles)
        return Result(404)  # 缓存未找到

    def set_user_session_key(self, user_id, session_key):
        """ 建立用户id到session key的映射 """
        _ = locale.get()
        cache_key = self._user_session_key_ck(user_id)
        self._set_cache(cache_key, session_key, timeout=0)
        return Result(200, _('successfully set user session key mapping'))

    def get_user_session_key(self, user_id):
        cache_key = self._user_session_key_ck(user_id)
        user_session_key = self._get_cache(cache_key)

        if user_session_key:
            return Result(200, data=user_session_key)
        return Result(404)   # 缓存未找到

    def clear_user_info(self, user_id):
        """ 清除用户所有缓存信息 """
        info_cache_key = self._user_info_ck(user_id)
        roles_cache_key = self._user_roles_ck(user_id)

        self._delete_cache(info_cache_key)  # 清理信息缓存
        self._delete_cache(roles_cache_key)  # 清理权限缓存
        return Result(200)

    def clear_user_session(self, user_id):
        """ 清理用户登录凭证，请注意此方法基于cookie-session模型，目前已经过期 """
        user_session_key_cache_key = self._user_session_key_ck(user_id)
        user_token_cache_key = self._discord_oauth_token_ck(user_id)

        self._delete_cache(user_session_key_cache_key)  # 清理会话映射缓存
        self._delete_cache(user_token_cache_key)  # 清理oauth2登录凭证
        return Result(200)

    def set_revoked_token(self, jti: str, ttl):
        """ 吊销某个token """
        cache_key = self._revoked_token_ck(jti)
        self._set_cache(cache_key, jti, timeout=ttl)

    def is_token_revoked(self, jti: str) -> bool:
        """ 检查token是否被吊销 """
        cache_key = self._revoked_token_ck(jti)
        return cache.get(cache_key) is not None

    @staticmethod
    def _set_cache(key, value, timeout=cache_timeout):
        """ 设置缓存 """
        cache.set(key, value, timeout=math.floor(timeout))

    @staticmethod
    def _get_cache(key):
        return cache.get(key)

    @staticmethod
    def _delete_cache(key):
        """ 删除缓存 """
        cache.delete(key)

cache_service = CacheService()