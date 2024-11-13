"""
权限校验蓝图
"""

from service import user_service
from flask import Blueprint, session, jsonify, request, g, abort
from requests_oauthlib import OAuth2Session

from utils import config, ConfigEnum, auth

auth_bp_v1 = Blueprint('auth_bp_v1', __name__, url_prefix='/api/v1/auth')

client_id = config.get(ConfigEnum.DISCORD_OAUTH_CLIENT_ID)
client_secret = config.get(ConfigEnum.DISCORD_OAUTH_CLIENT_SECRET)
discord_api_endpoint = config.get(ConfigEnum.DISCORD_API_ENDPOINT)
scope = config.get(ConfigEnum.DISCORD_OAUTH_SCOPE)
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
    if not auth.validate_login():
        # 用户未登录，构建重定向url响应到前端
        authorize_url = f'https://discord.com/api/oauth2/authorize?response_type=code&scope={scope}&client_id={client_id}&redirect_uri={redirect_uri}'
        return jsonify({'authorize_url': authorize_url}), 401  # 未登录

    # token存在执行用户权限校验
    session_token = session.get('discord_oauth_token')  # 检查用户登入状态
    user_id = session.get('user_id')  # 用户id

    if not user_id or not user_service.exist_user(user_id):  # 用户id不存在，或者即使用户id存在，数据库不存在
        oauth = OAuth2Session(token={'access_token': session_token.get('access_token')})
        response = oauth.get(f'{discord_api_endpoint}/users/@me')  # 请求用户数据

        if response.status_code != 200:  # 错误
            abort(response.status_code)

        # 成功拉取用户数据，将用户数据写入缓存和session
        session['user_id'] = response.json()['id']
        user_service.save_user(data=response.json())

    return jsonify({'message': _('Login success')}), 200  # 登录成功


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
            properties:
              message:
                type: string
                example: 'Authorize success'
      400:
        description: 参数错误
    """
    _ = g.t
    body = request.get_json()
    code = body.get('code')

    if not code or not redirect_uri:
        return abort(400)

    oauth = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
    access_token = oauth.fetch_token(
        code=code,
        client_secret=client_secret,
        token_url=f'{discord_api_endpoint}/oauth2/token'
    )

    # 设置会话信息
    session['discord_oauth_token'] = access_token
    return jsonify({'message': _('Authorize success')}), 200  # 认证成功


