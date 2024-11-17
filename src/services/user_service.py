from datetime import datetime
from functools import wraps

from flask import abort, jsonify, g
from clients import discord_oauth
from clients.discord_oauth import fetch_token
from core import session, cache, db
from dao import copy_properties, DiscordUser, to_dict, Role

users_prefix = 'users'
roles_prefix = 'roles'
info_prefix = 'info'

class CurrentUser:
    """
    当前用户，使用session来定位当前用户，并提供操作当前用户相关的api接口
    """
    @staticmethod
    def login(code):
        """
        操作用户的先决条件，下面提供的所有api都是假定在当前用户已经登入的情况下展开的
        如果当前用户没有登入而让用户接触到下面的api，那么会造成一些不可预期的后果
        :param code: 用户授权码
        """
        try:
            user_token = fetch_token(code)      # 拉取用户授权凭证
            access_token = user_token.get('access_token')
            user_data = discord_oauth.fetch_user(access_token)      # 拉取用户信息
        except RuntimeError: abort(401)

        user = db.session.get(DiscordUser, user_data['id'])
        if not user:
            # 用户不存在，创建新的用户数据
            user = DiscordUser()
            copy_properties(user_data, user)
            db.session.add(user)
            # 分配用户权限
            user_role = Role.query.filter_by(name='user').first()  # 用户级别权限
            # 未找到权限等级
            _ = g.t
            if not user_role:  # 权限未找到，数据库错误
                return jsonify({'message': _("'user role' not found")}), 500
            user.roles.append(user_role)
        else:
            # 用户已经存在，更新数据
            copy_properties(user_data, user)

        # 提交数据库
        db.session.commit()

        # 将用户关键字段id记入session
        session['discord_oauth_token'] = user_token
        session['user_id'] = user_data['id']

        # 将用户数据写入缓存
        cache.set(f'{users_prefix}:{user.id}:{info_prefix}', to_dict(user))
        # 将权限写入缓存
        cache.set(f'{users_prefix}:{user.id}:{roles_prefix}', user.roles)

    @staticmethod
    def get_info() -> dict:
        """ 获取当前用户信息 """
        user_id = session['user_id']
        user_info = cache.get(f'{users_prefix}:{user_id}:{info_prefix}')
        if user_info: return user_info  # 缓存存在用户数据直接返回

        # 缓存不存在，从数据库查询
        user = db.session.query(DiscordUser).get(user_id)
        if user:  # 用户存在，缓存数据
            user_info = to_dict(user)
            cache.set(f'{users_prefix}:{user_id}:{info_prefix}', user_info)
            return user_info
        abort(404)  # 用户不存在

    @staticmethod
    def get_roles():
        """ 获取当前用户权限 """
        user_id = session['user_id']
        user_roles = cache.get(f'{users_prefix}:{user_id}:{roles_prefix}')
        if user_roles: return user_roles

        # 缓存不存在，从数据库查询
        user = db.session.query(DiscordUser).get(user_id)
        if not user: abort(404)
        user_roles = user.roles
        if not user_roles: abort(404)
        return user_roles

    @staticmethod
    def has_role(role) -> bool:
        """
        当前用户是否拥有权限
        :param role: 权限名称
        """
        role = db.session.query(Role).filter_by(name=role).first()
        if not role: abort(404)

        if role == 'anonymous':
            return True  # 允许匿名

        roles = current_user.get_roles()
        if role in roles:
            return True
        abort(403)

    @staticmethod
    def is_active() -> bool:
        """ 当前用户账号状态是否激活 """
        user_info = current_user.get_info()
        if user_info: return user_info['is_active']
        abort(404)

    @staticmethod
    def is_login() -> bool:
        """ 当前用户是否登入 """
        session_token = session.get('discord_oauth_token', {})
        if not session_token:
            return False  # 无状态视为过期

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
                return False
        return True  # 会话有效，正常执行

    @staticmethod
    def login_required(func):
        """ 基于session的登陆状态检查 """
        @wraps(func)
        def decorated(*args, **kwargs):
            if not current_user.is_login(): abort(401)  # 当前用户未登入
            if not current_user.is_active(): abort(403)  # 当前用户被封禁
            return func(*args, **kwargs)  # 会话有效，正常执行
        return decorated

    @staticmethod
    def role_required(role):
        """ 基于session兼数据库的权限校验 """
        def decorator(func):
            @wraps(func)
            def decorated(*args, **kwargs):
                if not current_user.has_role(role):  abort(403)  # 当前用户没有足够权限
                return func(*args, **kwargs)
            return decorated
        return decorator

current_user = CurrentUser()








