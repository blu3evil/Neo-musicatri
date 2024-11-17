"""
权限校验蓝图
"""
from clients import discord_oauth
from services.user_service import current_user
from flask import Blueprint, jsonify, request, g, abort

from utils import config, ConfigEnum
from core import cache

auth_bp_v1 = Blueprint('auth_bp_v1', __name__, url_prefix='/api/v1/auth')

redirect_uri = config.get(ConfigEnum.DISCORD_OAUTH_REDIRECT_URI)

# 登入接口，检测用户是否登入，如果已经登入那么返回用户数据，否则返回重定向url指引用户登入
@auth_bp_v1.route('/login', methods=['GET'])
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
            properties:
              message:
                type: string
                example: 'Forbidden'
                description: 用户不具备登入的权限
    """
    _ = g.t
    if not current_user.is_login(): abort(401)  # 用户未登录
    if not current_user.is_active(): abort(403)  # 账号未激活
    return jsonify({ 'message': _('Login success') })  # 登录成功


# 提供前端请求获取认证url
@auth_bp_v1.route('/authorize-url', methods=['GET'])
@cache.cached(timeout=60)
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
    _ = g.t
    code = request.get_json().get('code')
    if not code: abort(400)  # 参数错误
    current_user.login(code)  # 执行登入
    return jsonify({ 'message': _('Authorize success') })  # 认证成功


# 会话检查接口，用于前端检查当前登入状态
@auth_bp_v1.route('/status', methods=['GET'])
@current_user.login_required
@current_user.role_required('user')
def status():
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
        description: 用户权限不足
    """
    _ = g.t
    return jsonify({ 'message': _('Logged in') })  # 认证通过