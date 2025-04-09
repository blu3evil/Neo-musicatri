from datetime import datetime
from functools import wraps

from oauthlib.oauth2 import InvalidGrantError

from common import Result
from auth_server.clients import discord_oauth

from auth_server.auth_server_context import context

from auth_server.services.user_service import user_service  # 用户服务
from auth_server.services.cache_service import cache_service  # 缓存服务
from auth_server.services.session_service import session_service  # 会话服务

from auth_server.domain.models import copy_properties, DiscordUser, to_dict, Role, db

session = context.session
config = context.config
locale = context.locale

class AuthService:
    """ 认证服务 """
    @staticmethod
    def user_login(code) -> Result:
        """
        操作用户的先决条件，下面提供的所有api都是假定在当前用户已经登入的情况下展开的
        如果当前用户没有登入而让用户接触到下面的api，那么会造成一些不可预期的后果
        :param code: 用户授权码
        """
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

        # 写入会话信息
        session_service.register_user_session(user_id=user_id, user_token=user_token)
        session_service.upsert_user_session(user_id=user_id)

        # 写入缓存信息
        cache_service.set_user_info(user_id=user_id, user_info=to_dict(user))
        role_names = [role.name for role in user.roles]  # 将权限写入缓存
        cache_service.set_user_roles(user_id=user_id, role_names=role_names)

        return Result(200)

    @staticmethod
    def user_logout(user_id) -> Result:
        """ 登出目标用户 """
        _ = locale.get()
        # session.clear()  # 清理session
        result = session_service.get_current_user_session_token()
        if result.code != 200: return result

        # 销毁登录凭证
        session_token = result.data['session_token']
        access_token = session_token['access_token']
        refresh_token = session_token['refresh_token']

        try:
            discord_oauth.revoke_access_token(access_token)  # 销毁access_token
            discord_oauth.revoke_access_token(refresh_token)  # 销毁refresh_token
        except RuntimeError:
            return Result(500, _('failed in revoking user session token'))

        result = session_service.unregister_user_session(user_id=user_id)
        if result.code != 200: return result

        result = cache_service.clear_user(user_id=user_id)  # 清理缓存
        if result.code != 200: return result

        return Result(200, _('user logged out'))  # 用户登出成功


    @staticmethod
    def verify_role(user_id, role: str) -> Result:
        """
        当前用户是否拥有权限
        :param role: 权限名称
        :param user_id: 用户id
        """
        if role == 'anonymous':
            return Result(200)  # 允许匿名
        _ = locale.get()
        role = db.session.query(Role).filter_by(name=role).first()
        if not role: return Result(500, _('role not found'))

        result = user_service.get_user_roles(user_id)
        if result.code != 200: return result  # 向上层传递result

        if role.name not in result.data:
            return Result(403, _('permission denied'))
        return Result(200, _("access granted"))

    @staticmethod
    def verify_login(user_id) -> Result:
        """ 检查用户是否登录 """
        _ = locale.get()
        result = cache_service.get_user_session_key(user_id)
        if result.code != 200:
            session.clear()  # 清理用户session
            return Result(401, _('session key not found'))  # 未发现session key

        result = session_service.get_current_user_session_token()
        if result.code != 200:
            return Result(401, _('session token not found'))  # 无状态视为过期

        session_token = result.data['session_token']

        # 检查账号激活状态
        result = user_service.get_user_info(user_id)
        if not result.code == 200: return result  # 向上传递result

        if not result.data.get('is_active'):
            return Result(403, _('account is not active'))

        expires_at = session_token.get('expires_at')
        current_time = int(datetime.now().timestamp())
        if expires_at < current_time:
            # 此时已经超过过期时间，会话过期，执行刷新token
            token = session_token.get('refresh_token')
            try:
                new_token = discord_oauth.refresh_token(token)
                # 将新的token写入session
                session['discord_oauth_token'] = new_token
            except RuntimeError:
                # refresh token过期或者无效
                return Result(401, _('refresh token failed'))
        return Result(200)  # 会话有效，正常执行

    # 权限校验装饰器
    @staticmethod
    def require_login(func):
        """ 基于session的登陆状态检查 """
        @wraps(func)
        def decorated(*args, **kwargs):
            result = auth_service.verify_login(session.get('user_id'))  # 检查登录状态
            if result.code == 200: return func(*args, **kwargs)  # 会话有效，正常执行
            else: return result.as_response()
        return decorated

    @staticmethod
    def require_role(role: str):
        """ 基于session兼数据库的权限校验 """
        def decorator(func):
            @wraps(func)
            def decorated(*args, **kwargs):
                result = auth_service.verify_role(session.get('user_id'), role)  # 校验用户权限
                if result.code == 200: return func(*args, **kwargs)
                else: return result.as_response()
            return decorated
        return decorator


auth_service = AuthService()  # 认证服务






