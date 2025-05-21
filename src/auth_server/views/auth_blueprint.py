""" 权限校验蓝图 """
from flask import Blueprint, jsonify, request, current_app

from auth_server.clients import discord_oauth
from auth_server.context import context, ServerAuthConfigKey
from auth_server.services.auth_service import user_auth_service_v1, user_auth_service_v2, service_auth_service_v2
from common.domain.models import Result

cache = context.cache
session = context.session
config = context.config
locale = context.locale

redirect_uri = config.get(ServerAuthConfigKey.DISCORD_OAUTH_REDIRECT_URI)

user_auth_bp_v1 = Blueprint('user_auth_bp_v1', __name__, url_prefix='/api/v1/auth')  # 基于cookie-session的登录校验

# 用户使用此接口尝试登录，若用户没有处于登录状态那么返回401，前端通过/authorize-url接口获取
# discord oauth2重定向链接并跳转引导用户进行oauth2登录认证
@user_auth_bp_v1.route('/login', methods=['GET'])
@user_auth_service_v1.login_required  # 校验用户登录权限
def user_login_v1():
    """
    用户登录接口
    ---
    tags:
      - 认证接口v1
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
      403:
        description: 用户登入请求被拒绝
    """
    _ = locale.get()
    return Result(200).as_response()


# 提供前端请求获取认证url
@user_auth_bp_v1.route('/authorize-url', methods=['GET'])
@cache.cached(timeout=3600)
def user_authorize_url():
    """
    授权链接接口
    ---
    tags:
      - 认证接口v1
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


@user_auth_bp_v1.route('/authorize', methods=['POST'])
def user_authorize_v1():
    """
    用户授权接口
    ---
    tags:
      - 认证接口v1
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
      403:
        description: 参数错误
    """
    _ = locale.get()
    code = request.get_json().get('code')
    if not code: return jsonify({ 'message': _('invalid argument') }), 403  # 参数错误

    result = user_auth_service_v1.login({
        'code': code
    })  # 执行登入
    return result.as_response()


# 会话检查接口，用于前端检查当前登入状态
@user_auth_bp_v1.route('/status', methods=['GET'])
@user_auth_service_v1.login_required
@user_auth_service_v1.role_required('user')
def user_verify_login():
    """
    用户登录状态检查接口
    ---
    tags:
      - 认证接口v1
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
    _ = locale.get()
    return jsonify({ 'message': _('Logged in') })  # 认证通过


# 权限校验接口，校验用户权限是否符合要求
@user_auth_bp_v1.route('/role/<role>', methods=['GET'])
@user_auth_service_v1.login_required
def user_verify_role(role):
    """
    用户权限等级校验接口
    ---
    tags:
      - 认证接口v1
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
    _ = locale.get()
    result = user_auth_service_v1.verify_role(role)  # 校验用户权限
    return result.as_response()


@user_auth_bp_v1.route('/logout', methods=['DELETE'])
@user_auth_service_v1.login_required
def user_logout_v1():
    """
    用户登出接口
    ---
    tags:
      - 认证接口v1
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
    result = user_auth_service_v1.logout()
    response = result.as_response()  # 删除cookie
    with current_app.app_context():
        session_cookie_name = current_app.config.get('SESSION_COOKIE_NAME', "session")  # 存储在浏览器端的cookie名
        response.delete_cookie(session_cookie_name)
    return response

user_auth_bp_v2 = Blueprint('user_auth_bp_v2', __name__, url_prefix='/api/v2/auth/user')  # 基于jwt的用户登录校验

# v2登录接口，此接口使用jwt设计，在认证成功后签发jwt
@user_auth_bp_v2.route('/login', methods=['GET'])
@user_auth_service_v2.validate_required()  # 校验用户登录权限
def user_login_v2():
    """
    用户校验接口
    ---
    tags:
      - 认证接口v2
    description: 用户使用此接口检查自身登录状态
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
      403:
        description: 用户登入请求被拒绝
    """
    _ = locale.get()
    return Result(200).as_response()


@user_auth_bp_v2.route('/authorize', methods=['POST'])
def user_authorize_v2():
    """
    用户授权接口
    ---
    tags:
      - 认证接口v2
    description: 作用在用户携带code执行认证
    responses:
      200:
        description: 用户授权成功，返回签发的jwt
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'Authorize success'
            data:
              type: object
              properties:
                access_token:
                  type: string
                  example: '<TOKEN>'
                token_type:
                  type: string
                  example: 'Bearer'
                expires_at:
                  type: string
                  example: '<exp>'
      403:
        description: 参数错误，未提交或oauth返回的code异常
    """
    _ = locale.get()
    code = request.get_json().get('code')
    if not code: return jsonify({ 'message': _('invalid argument') }), 403  # 参数错误

    result = user_auth_service_v2.login({
        'code': code
    })  # 执行登入
    return result.as_response()


@user_auth_bp_v2.route('/logout', methods=['DELETE'])
@user_auth_service_v2.validate_required()
def user_logout_v2():
    """
    用户登出接口
    ---
    tags:
      - 认证接口v2
    description: 前端执行退出逻辑时调用接口，此接口将会吊销用户的jwt
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
    result = user_auth_service_v2.logout()  # 吊销凭证
    return result.as_response()


@user_auth_bp_v2.route('/validate', methods=['POST'])
def user_validate_v2():
    """
    用户校验接口
    ---
    tags:
      - 认证接口v2
    description: 用于校验当前用户状态，包括登录状态以及权限级别
    parameters:
      - name: roles
        in: body
        type: array
        example: ['user', 'admin']
    responses:
      200:
        description: 用户具备目标状态
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'access granted'
            data:
              type: object
              properties:
                user_id:
                  type: string
                  example: '1'
                  description: 用户id，即discord用户id
                roles:
                  type: array
                  example: ['user', 'admin']
                  description: 当前用户权限级别
    """
    body = request.get_json()
    roles = body.get('roles', ['user'])  # 目标权限级别
    result = user_auth_service_v2.validate(roles)
    return result.as_response()


service_auth_bp_v2 = Blueprint('service_auth_bp_v2', __name__, url_prefix='/api/v2/auth/service')  # 基于jwt的服务校验
# v2服务端登录接口，支持服务间认证后api调用

@service_auth_bp_v2.route('/login', methods=['GET'])
@service_auth_service_v2.validate_required()  # 校验用户登录权限
def service_login_v2():
    """
    服务校验接口
    ---
    tags:
      - 认证接口v2
    description: 服务使用此接口来查询登录状态
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
      403:
        description: 用户登入请求被拒绝
    """
    _ = locale.get()
    return Result(200).as_response()


@service_auth_bp_v2.route('/authorize', methods=['POST'])
def service_authorize_v2():
    """
    服务授权接口
    ---
    tags:
      - 认证接口v2
    description: 服务使用此接口进行登录校验，获取服务间调用使用的jwt
    parameters:
      - name: credentials
        in: body
        type: object
        properties:
          client_id:
            type: string
            description: 服务id
          client_secret:
            type: string
            description: 服务密匙
    responses:
      200:
        description: 服务授权成功，返回签发的jwt
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'Authorize success'
            data:
              type: object
              properties:
                access_token:
                  type: string
                  example: '<TOKEN>'
                token_type:
                  type: string
                  example: 'Bearer'
                expires_at:
                  type: string
                  example: '<exp>'
      403:
        description: 参数错误，未提交或oauth返回的code异常
    """
    _ = locale.get()
    client_id = request.get_json().get('client_id')
    client_secret = request.get_json().get('client_secret')

    if not client_id or not client_secret:
        return jsonify({ 'message': _('invalid argument') }), 403  # 参数错误

    result = service_auth_service_v2.login({
        'client_id': client_id,
        'client_secret': client_secret
    })  # 执行登入
    return result.as_response()


@service_auth_bp_v2.route('/logout', methods=['DELETE'])
@service_auth_service_v2.validate_required()
def service_logout_v2():
    """
    服务登出接口
    ---
    tags:
      - 认证接口v2
    description: 此接口将会吊销服务的jwt，使服务jwt失效
    responses:
      200:
        description: 需要关闭某个服务时可以考虑调用
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'Service logged out successfully'
      401:
        description: 用户未登录
    """
    result = service_auth_service_v2.logout()  # 吊销凭证
    return result.as_response()


@service_auth_bp_v2.route('/validate', methods=['POST'])
def service_validate_v2():
    """
    服务校验接口
    ---
    tags:
      - 认证接口v2
    description: 用于校验当前服务状态，包括登录状态以及服务器所有权限级别
    parameters:
      - name: roles
        in: body
        type: array
        example: ['plain']
    responses:
      200:
        description: 用户具备目标状态
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'access granted'
            data:
              type: object
              properties:
                client_id:
                  type: string
                  example: '1'
                  description: 服务id，服务注册时的id
                roles:
                  type: array
                  example: ['plain']
                  description: 当前服务所拥有的权限级别
    """
    body = request.get_json()
    roles = body.get('roles', ['plain'])  # 目标权限级别
    result = service_auth_service_v2.validate(roles)
    return result.as_response()