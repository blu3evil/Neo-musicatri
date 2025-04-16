from utils.context import CacheConfigKey

from server_auth.context import context
from common import Result

# redis = context.py.redis  # redis客户端
config = context.config  # 配置
cache = context.cache
locale = context.locale

cache_timeout = config.get(CacheConfigKey.CACHE_TIMEOUT)

class CacheService:
    """ 缓存服务 """
    @staticmethod
    def _user_info_cache_key(user_id):
        """ 用户数据缓存键名 """
        return f'users:{user_id}:info'

    @staticmethod
    def _user_roles_cache_key(user_id):
        """ 用户权限缓存键名 """
        return f'users:{user_id}:roles'

    @staticmethod
    def _user_session_key_cache_key(user_id):
        """ 用户id到session_key键名，用于建立用户id到session的映射 """
        return f'users:{user_id}:session'

    def set_user_info(self, user_id, user_info: dict):
        """ 建立用户数据信息缓存 """
        cache_key = self._user_info_cache_key(user_id)
        self._set_cache(cache_key, user_info)  # 将用户数据写入缓存
        return Result(200)

    def get_user_info(self, user_id):
        """ 获取用户信息缓存 """
        _ = locale.get()
        cache_key = self._user_info_cache_key(user_id)
        user_info = self._get_cache(cache_key)

        if user_info:
            return Result(200, data=user_info, message=_('hit cache'))
        return Result(404)  # 缓存未找到用户数据

    def set_user_roles(self, user_id, role_names: list):
        """ 建立用户权限信息缓存 """
        _ = locale.get()
        cache_key = self._user_roles_cache_key(user_id)
        self._set_cache(cache_key, role_names)
        return Result(200, _('successfully set user role into cache'))

    def get_user_roles(self, user_id):
        """ 获取用户权限缓存 """
        _ = locale.get()
        cache_key = self._user_roles_cache_key(user_id)
        user_roles = self._get_cache(cache_key)

        if user_roles: return Result(200, _('hit cache'), user_roles)
        return Result(404)  # 缓存未找到

    def set_user_session_key(self, user_id, session_key):
        """ 建立用户id到session key的映射 """
        _ = locale.get()
        cache_key = self._user_session_key_cache_key(user_id)
        self._set_cache(cache_key, session_key, permanent=True)
        return Result(200, _('successfully set user session key mapping'))

    def get_user_session_key(self, user_id):
        cache_key = self._user_session_key_cache_key(user_id)
        user_session_key = self._get_cache(cache_key)

        if user_session_key:
            return Result(200, data={'user_session_key': user_session_key})
        return Result(404)   # 缓存未找到

    def clear_user(self, user_id):
        """ 清除用户所有缓存信息 """
        info_cache_key = self._user_info_cache_key(user_id)
        roles_cache_key = self._user_roles_cache_key(user_id)
        self._delete_cache(info_cache_key)  # 清理信息缓存
        self._delete_cache(roles_cache_key)  # 清理权限缓存
        return Result(200)

    def clear_user_session_key(self, user_id):
        """ 清理用户登录凭证 """
        user_session_key = self._user_session_key_cache_key(user_id)
        self._delete_cache(user_session_key)  # 清理会话映射缓存
        return Result(200)

    @staticmethod
    def _set_cache(key, value, permanent=False):
        """ 设置缓存 """
        cache.set(key, value, timeout=0 if permanent else cache_timeout)

    @staticmethod
    def _get_cache(key):
        return cache.get(key)

    @staticmethod
    def _delete_cache(key):
        """ 删除缓存 """
        cache.delete(key)

cache_service = CacheService()