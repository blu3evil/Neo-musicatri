from datetime import datetime
import math

from typing_extensions import deprecated

from common.utils.context import CacheConfigKey

from auth_server.context import context
from common.domain.models import Result
from flask_jwt_extended import decode_token


# redis = auth_client.py.redis  # redis客户端
config = context.config  # 配置
cache = context.cache
locale = context.locale
logger = context.logger

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
    def _access_token_ck(user_id: str):
        """ 用户id到jwt的映射键名，当外部需要获取用户token时可以获取 """
        return f'users:{user_id}:access_token'

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

    def set_user_token(self, user_id, token: str) -> Result:
        """
        建立用户id到access token列表的缓存，维护一个用户可能存在多个access token的情况
        """
        _ = locale.get()
        cache_key = self._access_token_ck(user_id)
        tokens = cache.get(cache_key) or []
        if token not in tokens:
            tokens.append(token)
            try:
                jwt_payload = decode_token(token)
                exp_timestamp = jwt_payload.get('exp')

                if exp_timestamp:
                    # 将过期时间转换为剩余时间（单位为秒）
                    expires_at = datetime.utcfromtimestamp(exp_timestamp) - datetime.utcnow()
                    # 将剩余过期时间作为缓存超时时间
                    cache.set(cache_key, tokens, timeout=int(expires_at.total_seconds()))
                else:
                    # 如果没有找到 'exp' 字段，默认设置较长过期时间
                    cache.set(cache_key, tokens, timeout=3600)  # 设置为1小时

            except Exception as e:
                # 如果解码失败，处理异常
                logger.error(f"Error decoding token: {str(e)}")
                return Result(500, message=_('failed to decode JWT'))

        return Result(200, message=_("Token stored successfully"))

    def get_user_tokens(self, user_id: str) -> Result:
        """ 获取用户有效的 access token 列表，并清理过期的 token """
        cache_key = self._access_token_ck(user_id)

        tokens = cache.get(cache_key) or []  # 获取 token 列表，默认空列表
        valid_tokens = []
        latest_exp = None  # 用户所有有效token中有效时间最长的token

        for access_token in tokens:
            try:
                jwt_payload = decode_token(access_token)
                jti = jwt_payload.get('jti')
                if jti and self.is_token_revoked(jti):
                    continue  # jwt过期，跳过此jwt

                exp_timestamp = jwt_payload.get('exp')
                if exp_timestamp:
                    exp_time = datetime.utcfromtimestamp(exp_timestamp)
                    if exp_time > datetime.utcnow():
                        valid_tokens.append(access_token)
                        if latest_exp is None or exp_time > latest_exp:
                            latest_exp = exp_time
                else:
                    # 没有 exp 字段，认为有效（但极少见）
                    valid_tokens.append(access_token)

            except Exception as e:
                logger.error(f"Error decoding token: {str(e)}")
                continue  # 跳过非法 token

        # 如果发现 token 有所变化（即清理了），更新缓存
        if len(valid_tokens) != len(tokens):
            timeout = int((latest_exp - datetime.utcnow()).total_seconds()) if latest_exp else 3600
            cache.set(cache_key, valid_tokens, timeout=timeout)

        if valid_tokens:
            return Result(200, data={'tokens': valid_tokens}, message="Successfully retrieved valid tokens.")
        else:
            return Result(404, message="No valid tokens found.")


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

    @deprecated('using token rather than cookie session')
    def clear_user_session(self, user_id):
        """ 清理用户登录凭证，请注意此方法基于cookie-session模型，目前已经过期 """
        user_session_key_cache_key = self._user_session_key_ck(user_id)
        user_token_cache_key = self._discord_oauth_token_ck(user_id)

        self._delete_cache(user_session_key_cache_key)  # 清理会话映射缓存
        self._delete_cache(user_token_cache_key)  # 清理oauth2登录凭证
        return Result(200)

    def clear_user_token(self, user_id) -> Result:
        _ = locale.get()
        result = self.get_user_tokens(user_id)
        if result.code != 200: return result

        tokens = result.data['tokens']
        for token in tokens:
            try:
                jwt_payload = decode_token(token)
                jti = jwt_payload.get('jti')
                exp = jwt_payload.get('exp')  # 这是 Unix 时间戳
                if not jti or not exp:
                    continue  # 缺失信息的 token 无法吊销

                ttl = max(0, int(exp - datetime.utcnow().timestamp()))
                self.set_revoked_token(jti, ttl)  # 逐个吊销token

            except Exception as e:
                logger.error(f"Error decoding token: {str(e)}")
                continue

        result = self.get_user_tokens(user_id)  # 触发token清理逻辑
        if result.code == 404:
            # 404代表全部清除
            return Result(200, message=_("All tokens cleared."))
        return Result(500, _("illegal status while clearing tokens"))

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