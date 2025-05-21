import abc
import uuid
from abc import abstractmethod, ABC
from datetime import datetime
from functools import wraps

from oauthlib.oauth2 import InvalidGrantError

from common.domain.models import Result
from auth_server.clients import discord_oauth

from auth_server.context import context

from auth_server.services.user_service import user_service_v1  # 用户服务
from auth_server.services.cache_service import cache_service, cache  # 缓存服务
from auth_server.services.session_service import session_service  # 会话服务

from auth_server.domain.models import copy_properties, DiscordUser, model_to_dict, Role, db

session = context.session
config = context.config
locale = context.locale
logger = context.logger

user_login_type = "discord_user"

class AuthService(abc.ABC):
    """
    认证服务接口抽象父类，提供有关权限校验相关api，例如discord认证流以及discord token校验
    """
    @staticmethod
    def _process_discord_login(code) -> Result:
        """ 执行discord登录流程，主要是discordOauth2认证，方法返回user信息以及认证token """
        _ = locale.get()
        try:
            user_token = discord_oauth.fetch_token(code)  # 拉取用户授权凭证
            access_token = user_token.get('access_token')  # 通过凭证获取access_token
            user_data = discord_oauth.fetch_user(access_token)  # 拉取用户信息
        except InvalidGrantError:  # code异常
            return Result(400, _('Invalid code'))
        except RuntimeError:
            return Result(500, _('Cannot fetch user access token'))

        user_id = user_data['id']
        user = db.session.get(DiscordUser, user_id)
        if not user:
            # 用户不存在，创建新的用户数据
            user = DiscordUser()
            copy_properties(user_data, user)
            db.session.add(user)
            # 分配用户权限
            user_role = Role.query.filter_by(name='user').first()  # 用户级别权限
            # 未找到权限等级
            if not user_role:  # 权限未找到，数据库错误
                return Result(500, _("'user role' not found"))
            user.roles.append(user_role)  # 为用户添加权限
        else:
            # 用户已经存在，更新数据
            copy_properties(user_data, user)

        # 提交数据库
        db.session.commit()
        cache_service.set_discord_oauth_token(user_id=user_id, user_token=user_token)  # 将令牌写入缓存

        return Result(200, data={
            'user': model_to_dict(user),
            'user_token': user_token
        })  # 返回用户信息以及token

    @staticmethod
    def _process_discord_token_validate(user_id) -> Result:
        """
        discord token自校验刷新逻辑，在校验用户登录状态时应该调用此方法对缓存中存储的discord oauth认证
        令牌进行有效性判断，并在令牌失效时进行执行刷新
        """
        _ = locale.get()
        result = cache_service.get_discord_oauth_token(user_id)
        if result.code != 200:
            return Result(401, _('illegal user token'))  # 无状态视为过期

        user_token = result.data
        expires_at = user_token.get('expires_at')
        current_time = int(datetime.now().timestamp())
        if expires_at < current_time:
            # 此时已经超过过期时间，会话过期，执行刷新token
            token = user_token.get('refresh_token')
            try:
                new_token = discord_oauth.refresh_token(token)  # 将新的token写入cache
                cache_service.set_discord_oauth_token(user_id=user_id, token=new_token)
                # session['discord_oauth_token'] = new_token
            except RuntimeError:  # refresh token过期或者无效
                return Result(401, _('refresh token failed'))
        return Result(200)  # 令牌有效

    @abstractmethod
    def login(self, credentials: dict) -> Result:
        """
        登录当前用户，基于discord oauth2回调构建的code码进行登录校验，在用户调用此方法成功登陆后
        应当存在策略记录当前用户的登陆状态

        :param credentials: 登录凭证
        """
        pass

    @abstractmethod
    def logout(self) -> Result:
        """
        登出当前用户，需要销毁基于user_login登录方法创建的用户登录凭证，从而撤销用户的登录状态
        """
        pass


class CookieSessionAuthService(AuthService, ABC):
    def verify_login(self) -> Result:
        """ 校验当前用户登录状态 """
        _ = locale.get()
        return Result(500, _('block gateway'))

    def verify_role(self, role: str) -> Result:
        """ 校验当前用户权限等级 """
        _ = locale.get()
        return Result(500, _('block gateway'))

    # 权限校验装饰器
    def login_required(self, func):
        """ 调用自身的verify_login方法对接口进行拦截登录校验 """
        @wraps(func)
        def decorated(*args, **kwargs):
            result = self.verify_login()  # 检查登录状态
            if result.code == 200: return func(*args, **kwargs)  # 会话有效，正常执行
            else: return result.as_response()
        return decorated

    def role_required(self, role: str):
        """ 调用自身的verify_role方法对接口进行拦截权限校验 """
        def decorator(func):
            @wraps(func)
            def decorated(*args, **kwargs):
                result = self.verify_role(role)  # 校验用户权限
                if result.code == 200: return func(*args, **kwargs)
                else: return result.as_response()
            return decorated
        return decorator


class UserAuthServiceV1(CookieSessionAuthService):
    """ 基于cookie-session的认证服务 """
    def login(self, credentials: dict) -> Result:
        """
        基于cookie-session的登录逻辑，在完成discord oauth2认证回调之后存储用户session信息，
        记录登录状态
        """
        _ = locale.get()
        code = credentials.get('code')
        if not code:
            return Result(401, _('invalid code'))

        result = self._process_discord_login(code)
        if result.code != 200: return result

        user = result.data.get('user')
        user_id = user.get('id')  # 用户id
        user_token = result.data.get('user_token')  # discord oauth2令牌
        role_names = [role.get('name') for role in user.get('roles')]

        session_service.register_user_session(user_id=user_id)  # 将用户id写入session
        session_service.upsert_user_session(user_id=user_id)  # 更新userid到session_id映射

        # 写入用户缓存信息
        cache_service.set_user_info(user_id=user_id, user_info=user)
        cache_service.set_user_roles(user_id=user_id, role_names=role_names)

        return Result(200)

    def logout(self) -> Result:
        """ 登出当前用户 """
        _ = locale.get()
        result = session_service.get_current_user_id()
        if result.code != 200: return result
        user_id = result.data['user_id']

        result = cache_service.get_discord_oauth_token(user_id=user_id)
        if result.code != 200: return result

        # 销毁登录凭证
        session_token = result.data
        access_token = session_token['access_token']
        refresh_token = session_token['refresh_token']

        try:
            discord_oauth.revoke_access_token(access_token)  # 销毁access_token
            discord_oauth.revoke_access_token(refresh_token)  # 销毁refresh_token
        except RuntimeError:
            return Result(500, _('failed in revoking user session token'))

        result = cache_service.clear_user_session(user_id=user_id)
        if result.code != 200: return result

        result = cache_service.clear_user_info(user_id=user_id)  # 清理缓存
        if result.code != 200: return result

        session.clear()  # 清理session

        return Result(200, _('user logged out'))  # 用户登出成功

    def verify_role(self, role: str) -> Result:
        """
        校验当前用户是否拥有权限
        :param role: 权限名称
        """
        if role == 'anonymous':
            return Result(200)  # 允许匿名
        _ = locale.get()
        role = db.session.query(Role).filter_by(name=role).first()
        if not role: return Result(500, _('role not found'))

        result = session_service.get_current_user_id()
        if result.code != 200: return result
        user_id = result.data['user_id']

        result = user_service_v1.get_user_roles(user_id)
        if result.code != 200: return result  # 向上层传递result

        if role.name not in result.data:
            return Result(403, _('permission denied'))
        return Result(200, _("access granted"))

    def verify_login(self) -> Result:
        """
        检查校验当前用户是否登录
        """
        _ = locale.get()
        result = session_service.get_current_user_id()
        if result.code != 200:
            return self._login_failed(401, _('illegal user session'))  # 未发现用户id

        user_id = result.data['user_id']
        result = cache_service.get_user_session_key(user_id)
        if result.code != 200:
            return self._login_failed(401, _('illegal user session cache'), user_id)  # 未发现session key

        result = user_service_v1.get_user_info(user_id)  # 检查账号激活状态
        if result.code != 200:
            return self._login_failed(401, _('user info not found'), user_id)

        if not result.data.get('is_active'):
            return self._login_failed(403, _('account is not active'), user_id)

        result = self._process_discord_token_validate(user_id=user_id)
        if result.code != 200:
            return self._login_failed(result.code, result.message, user_id)

        # 登录校验成功，更新用户id到session_key的映射
        session_service.upsert_user_session(user_id=user_id)  # 更新userid到session_id映射
        return Result(200)  # 会话有效，正常执行

    @staticmethod
    def _login_failed(code, message, user_id=None) -> Result:
        session.clear()
        if user_id: cache_service.clear_user_session(user_id=user_id)  # 清理用户会话缓存信息
        return Result(code, message)

from flask_jwt_extended import create_access_token, verify_jwt_in_request, get_jwt_identity, get_jwt
jwt = context.jwt  # jwt

class JWTSessionAuthService(AuthService, ABC):
    """ 基于jwt的登录校验逻辑 """
    def validate(self, roles=None) -> Result:
        """
        同时校验用户的登陆状态以及权限级别，通过传入参数roles来指定校验的权限级别，校验
        权限级别之前会先校验用户的登陆状态

        完成校验之后返回此用户的id以及权限级别，可用于接口进行后续判断，相关参数以字典的形式
        注入被装饰的方法形参当中
        """
        pass

    def validate_required(self, roles: list[str]=None):
        """ 用户状态校验 """
        def decorator(func):
            @wraps(func)
            def decorated(*args, **kwargs):
                result = self.validate(roles)  # 校验用户权限
                if result.code == 200: return func(*args, **kwargs)
                else: return result.as_response()
            return decorated
        return decorator

    @staticmethod
    def revoke_token():
        """ 撤销token """
        _ = locale.get()

        token = get_jwt()
        jti = token.get('jti')
        exp = token.get('exp')

        if not jti or not exp: return Result(400, _("Invalid token"))
        logger.debug(f'revoke token: jti: {jti}, exp: {exp}')

        now = int(datetime.utcnow().timestamp())
        ttl = exp - now

        if ttl <= 0: return Result(400, _("Token already expired"))  # 凭证已经过期

        cache_service.set_revoked_token(jti, ttl)
        return Result(200, _("Token revoked successfully"))

    # @jwt.token_in_blocklist_loader
    # def validate_token(self, decrypted_token) -> bool:
    #     jti = decrypted_token['jti']
    #     return cache_service.is_token_revoked(jti)  # 通过缓存检查token是否已经被撤销


from datetime import timedelta
import inspect
class UserAuthServiceV2(JWTSessionAuthService):
    """ 基于jwt的登录校验 """
    jwt_type = "user"

    def login(self, credentials) -> Result:
        """ 基于jwt的登录逻辑，完成discord oauth2回调认证之后签发jwt，记录登录状态 """
        _ = locale.get()
        code = credentials.get('code')
        if not code: return Result(401, _('bad credentials'))

        result = self._process_discord_login(code)
        if result.code != 200: return result

        user = result.data.get('user')  # 用户信息
        user_token = result.data.get('user_token')  # discord oauth2令牌

        user_id = user.get('id')  # 用户id
        role_names = [role.get('name') for role in user.get('roles')]

        # 写入用户缓存信息
        cache_service.set_user_info(user_id=user_id, user_info=user)
        cache_service.set_user_roles(user_id=user_id, role_names=role_names)

        # 将jwt设置与discord access token同样的过期时间，默认为7天
        expires_at = user_token.get('expires_at', 604800)
        jwt_payload = {
            'jti': str(uuid.uuid4()),
            'type': UserAuthServiceV2.jwt_type  # 用户端jwt
        }

        access_token = create_access_token(
            identity=user_id,
            additional_claims=jwt_payload,
            expires_delta=timedelta(seconds=expires_at)
        )

        cache_service.set_user_token(user_id=user_id, token=access_token)  # 存储用户token

        return Result(200, data={
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_at': expires_at
        }, message=_("Authorize success"))  # 签发jwt

    def logout(self) -> Result:
        """ 用户登出 """
        _ = locale.get()
        result = self.revoke_token()  # 撤销用户登录令牌
        if result.code != 200:
            return result  # 如果撤销失败，返回错误信息
        return Result(200, _("User logged out successfully"))

    def _validate_login(self) -> Result:
        """ 校验用户登录状态 """
        try:
            _ = locale.get()

            verify_jwt_in_request()  # 校验jwt有效性
            user_id = get_jwt_identity()  # 获取jwt标识符，此处为用户id
            jwt_payload = get_jwt()  # 获取payload

            if not user_id:  # 用户id不存在
                return Result(401, _('invalid identity'))

            if jwt_payload.get('type') != UserAuthServiceV2.jwt_type:
                return Result(403, _('invalid token type'))

            result = user_service_v1.get_user_info(user_id)  # 检查账号激活状态
            if result.code != 200:
                return Result(401, _('user info not found'))

            if not result.data.get('is_active'):
                return Result(403, _('account is not active'))

            result = self._process_discord_token_validate(user_id=user_id)
            if result.code != 200: return result
            return Result(200, data={
                'user_id': user_id
            })  # 登录校验成功

        except Exception as e:
            # NoAuthorizationError, ExpiredSignatureError...
            # 抛出异常代表jwt校验失败
            return Result(401, f'not logged in: {str(e)}')

    @staticmethod
    def _validate_role(user_id, roles: list[str]) -> Result:
        """ 校验用户权限等级，同时返回用户拥有的权限级别 """
        _ = locale.get()

        result = user_service_v1.get_user_roles(user_id)
        if result.code != 200: return result
        role_names = result.data  # 查询用户权限级别

        code = 200
        message = _('access granted')

        for role_name in roles:
            role = db.session.query(Role).filter_by(name=role_name).first()
            if not role: return Result(500, _('role not found'))

            if role.name not in role_names:
                code = 403
                message = _('permission denied')
                break

        return Result(code, message, data={ 'roles': role_names })

    def validate(self, roles=None):
        """
        同时校验用户的登陆状态以及权限级别，通过传入参数roles来指定校验的权限级别，校验
        权限级别之前会先校验用户的登陆状态

        完成校验之后返回此用户的id以及权限级别，可用于接口进行后续判断，相关参数以字典的形式
        注入被装饰的方法形参当中
        """
        _ = locale.get()
        roles = ['user'] if roles is None else roles

        result = self._validate_login()  # 校验用户登录状态
        if result.code != 200: return result
        user_id = result.data.get('user_id')  # 用户id

        result = self._validate_role(user_id, roles)  # 校验用户权限级别
        if result.code != 200:
            result.data['user_id'] = user_id
            return result

        roles = result.data.get('roles')  # 用户权限级别
        return Result(200, data={
            'user_id': user_id,
            'roles': roles
        }, message=_('access granted'))  # 返回热数据

    def validate_required(self, roles: list[str]=None):
        """ 用户状态校验 """
        def decorator(func):
            @wraps(func)
            def decorated(*args, **kwargs):
                result = self.validate(roles)  # 校验用户权限
                if result.code == 200:
                    current_user_id = result.data.get('user_id')
                    current_user_roles = result.data.get('roles')

                    current_user = {
                        'user_id': current_user_id,
                        'roles': current_user_roles
                    }

                    sig = inspect.signature(func)
                    params = sig.parameters  # 获取被装饰函数的参数名

                    if 'current_user' in params:  # 如果被装饰的方法签名包含user_id，则传递它
                        return func(*args, **kwargs, current_user=current_user)

                    return func(*args, **kwargs)
                else:
                    return result.as_response()
            return decorated
        return decorator

CLIENT_SECRETS = {
    'bot-server': 'eh0woSw6tRlzzl2b4oCXHFQRm0ByrxWwJKE4S-Jfk7Y=',
    'file-server': 'uIwMgEc9tBn6D6_u0BqHBY9DBLSKvLvyvywGZ_pwP98='
}

class ServiceAuthServiceV2(JWTSessionAuthService):
    jwt_type = "service"

    def validate(self, roles=None) -> Result:
        """
        校验服务权限级别
        """
        _ = locale.get()
        roles = ['plain'] if roles is None else roles

        result = self._validate_login()  # 校验服务登录状态
        if result.code != 200: return result
        client_id = result.data.get('client_id')  # 用户id

        result = self._validate_role(roles)  # 校验用户权限级别
        if result.code != 200:
            result.data['client_id'] = client_id
            return result

        roles = result.data.get('roles')  # 用户权限级别
        return Result(200, data={
            'client_id': client_id,
            'roles': roles
        }, message=_('access granted'))  # 返回热数据

    @staticmethod
    def _validate_login() -> Result:
        """ 校验用户登录状态 """
        try:
            _ = locale.get()
            verify_jwt_in_request()  # 校验jwt有效性
            client_id = get_jwt_identity()  # 获取jwt标识符，此处为用户id

            jwt_payload = get_jwt()  # 获取payload

            if not client_id:  # 服务id不存在
                return Result(401, _('invalid identity'))

            if jwt_payload.get('type') != ServiceAuthServiceV2.jwt_type:
                return Result(403, _('invalid token type'))

            return Result(200, data={
                'client_id': client_id
            })  # 登录校验成功

        except Exception as e:
            # NoAuthorizationError, ExpiredSignatureError...
            # 抛出异常代表jwt校验失败
            return Result(401, f'not logged in: {str(e)}')

    @staticmethod
    def _validate_role(roles: list[str]) -> Result:
        """ 校验用户权限等级，同时返回用户拥有的权限级别 """
        _ = locale.get()

        jwt_payload = get_jwt()  # 获取payload
        role_names = jwt_payload.get('roles')  # 查询用户权限级别

        code = 200
        message = _('access granted')

        for role_name in roles:
            if role_name not in role_names:
                code = 403
                message = _('permission denied')
                break

        return Result(code, message, data={ 'roles': role_names })

    def login(self, credentials) -> Result:
        _ = locale.get()
        client_id = credentials.get('client_id')
        client_secret = credentials.get('client_secret')

        stored_secret = CLIENT_SECRETS.get(client_id)
        if stored_secret is None or stored_secret != client_secret:
            return Result(401, _('invalid credentials'))

        # jwt设置过期时间为7天
        expires_at = 604800
        jwt_payload = {
            'jti': str(uuid.uuid4()),
            'type': ServiceAuthServiceV2.jwt_type,  # 用户端jwt
            'roles': ['plain']  # 默认权限
        }

        access_token = create_access_token(
            identity=client_id,
            additional_claims=jwt_payload,
            expires_delta=timedelta(seconds=expires_at)
        )

        return Result(200, data={
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_at': expires_at
        }, message=_("Authorize success"))  # 签发jwt

    def logout(self) -> Result:
        _ = locale.get()
        result = self.revoke_token()  # 撤销用户登录令牌
        if result.code != 200:
            return result  # 如果撤销失败，返回错误信息
        return Result(200, _("Service logged out successfully"))


user_auth_service_v1 = UserAuthServiceV1()  # 认证服务v1

user_auth_service_v2 = UserAuthServiceV2()  # 用户认证服务v2
service_auth_service_v2 = ServiceAuthServiceV2()  # 服务认证服务v2








