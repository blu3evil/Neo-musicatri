""" 权限校验蓝图 """
from flask import Blueprint, jsonify, request

from clients import discord_oauth
from core import cache, session
from services.auth_service import auth_service
from utils import config, ConfigEnum, locales

auth_bp_v1 = Blueprint('auth_bp_v1', __name__, url_prefix='/api/v1/auth')
redirect_uri = config.get(ConfigEnum.DISCORD_OAUTH_REDIRECT_URI)

# 登入接口，检测用户是否登入，如果已经登入那么返回用户数据，否则返回重定向url指引用户登入
@auth_bp_v1.route('/login', methods=['GET'])
@auth_service.require_login  # 校验用户登录权限
def login():
    """
    用户登录接口
    ---
    tags:
      - 认证接口
    description: 作用在用户登入
    responses:
      200:
        description: 登录成功，自动更新、记录用户信息
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'Login success'
      401:
        description: 用户未认证
        schema:
          type: object
          properties:
            authorize_url:
              type: string
              example: 'https://discord.com/api/oauth2/authorize'
              description: 前端使用此url为用户执行跳转，获取discord授权码

      403:
        description: 用户登入请求被拒绝
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'Forbidden'
              description: 用户不具备登入的权限
    """
    _ = locales.get()
    return jsonify({ 'message': _('Login success') })  # 登录成功


# 提供前端请求获取认证url
@auth_bp_v1.route('/authorize-url', methods=['GET'])
@cache.cached(timeout=3600)
def authorize_url():
    """
    授权链接接口
    ---
    tags:
      - 认证接口
    description: 提供前端获取认证链接
    responses:
      200:
        description: 成功获取授权链接
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                authorize_url:
                  type: string
                  example: 'https://discord.com/api/oauth2/authorize'
    """
    url = discord_oauth.get_authorize_url()
    return jsonify({ 'data': { 'authorize_url': url } })  # 成功获取认证url


@auth_bp_v1.route('/authorize', methods=['POST'])
def authorize():
    """
    用户授权接口
    ---
    tags:
      - 认证接口
    description: 作用在用户携带code执行认证
    responses:
      200:
        description: 用户授权成功
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'Authorize success'
      400:
        description: 参数错误
    """
    _ = locales.get()
    code = request.get_json().get('code')
    if not code: return jsonify({ 'message': _('invalid argument') }), 403  # 参数错误

    result = auth_service.user_login(code)  # 执行登入
    return result.as_response()


# 会话检查接口，用于前端检查当前登入状态
@auth_bp_v1.route('/status', methods=['GET'])
@auth_service.require_login
@auth_service.require_role('user')
def verify_login():
    """
    用户登录状态检查接口
    ---
    tags:
      - 认证接口
    description: 用于前端检查用户登陆状态执行路由守卫
    responses:
      200:
        description: 用户已经登入
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'Logged in'
      401:
        description: 用户未登录
      403:
        description: 用户权限不足（至少需要用户级别权限）
    """
    _ = locales.get()
    return jsonify({ 'message': _('Logged in') })  # 认证通过


# 权限校验接口，校验用户权限是否符合要求
@auth_bp_v1.route('/role/<role>', methods=['GET'])
@auth_service.require_login
def verify_role(role):
    """
    用户权限等级校验接口
    ---
    tags:
      - 认证接口
    description: 用于前端查询用户当前是否满足某一权限等级要求
    responses:
      200:
        description: 用户权限等级符合要求
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'Access granted'
      401:
        description: 用户未登录
      403:
        description: 用户权限不足
    """
    _ = locales.get()
    user_id = session.get('user_id')
    result = auth_service.verify_role(user_id, role)  # 校验用户权限
    return result.as_response()


@auth_bp_v1.route('/logout', methods=['DELETE'])
@auth_service.require_login
def logout():
    """
    用户登出接口
    ---
    tags:
      - 认证接口
    description: 前端执行退出逻辑时调用接口，清除用户缓存信息和session
    responses:
      200:
        description: 用户登出成功，前端可以断开socketio连接
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'User logged out'
      401:
        description: 用户未登录
    """
    user_id = session.get('user_id')
    result = auth_service.user_logout(user_id)
    return result.as_response()