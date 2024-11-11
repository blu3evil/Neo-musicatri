"""
认证接口
"""""
from flask import Blueprint, Response, jsonify
from injector import inject

from services.abs.auth_service import AuthService

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')


@inject
@auth_bp.route('/login', methods=['POST'])
def auth_code_authenticate(auth_service: AuthService) -> Response:
    """
        用户授权码登录接口
        ---
        tags:
          - 认证接口
        description: |
          用户登录主要接口，Musicatri授权依赖于discord第三方授权，因此这个登录接口依赖于discord第三方授权，并在
          授权通过之后向前端返回一个jwt以及httponly的refresh token供往后的登录校验，依赖于前端的参数传递来执行
          不同形式的认证策略
        parameters:
          - name: code
            in: body
            required: true
            description: discord授权码，用于拉取用户信息进行校验
            type: string
            example: "<code>"
          - name: device_id
            in: header
            required: true
            description: 设备id号，由前端生成后在授权时发送，用于标识统一用户不同设备
            type: string
            example: "<device_id>"
          - name: Accept-Language
            in: header
            required: false
            description: 指定后端响应使用的本地化语言
            type: string
            example: "en-US"
        responses:
          20000:
            description: 用户授权成功
            schema:
              type: object
              properties:
                code:
                  type: int
                  example: 20000
                  description: 响应状态码
                access_token:
                  type: string
                  example: "<access_token>"
                  description: 用户登录使用的access token凭据，可用于跳过discord验证流程
                refresh_token:
                  type: string
                  example: "<refresh_token>"
                  description: 刷新token，用于刷新access token的有效期，当access token过期时使用
                expires_in:
                  type: int
                  example: 6000
                  description: access token的过期时间，access token过期后可使用refresh token刷新
          40001:
            description: |
              非法参数提交，通常是由于没有遵循给定的参数提交格式，认证接口接受code、access_token、refresh_token
              作为参数提交，并在三者之中优先选择code进行校验，其次是access_token
            schema:
              type: object
              properties:
                code:
                  type: integer
                  example: 40001
                  description: 参数非法
                message:
                  type: string
                  example: "<error_message>"
                  description: 参数异常
          40003:
            description: |
              权限拒绝，用户账号已经被禁止登录，无法调用此接口
            schema:
              type: object
              properties:
                code:
                  type: integer
                  example: 40003
                  description: 权限拒绝
                message:
                  type: string
                  example: "<error_message>"
                  description: 拒绝登入
          40006:
            description: |
              用户会话已经被关闭，这意味着access token以及refresh token已经失效，前端在接受到
              此响应码之后应当直接执行discord auth code认证工作流
            schema:
              type: object
              properties:
                code:
                  type: integer
                  example: 40006
                  description: token会话已经被关闭
                message:
                  type: string
                  example: "<error_message>"
                  description: 会话被关闭
          50000:
            description: |
              服务器内部错误导致无法正常执行授权流程，出错的原因可能为数据库连接、discord请求超时等
            schema:
              type: object
              properties:
                code:
                  type: integer
                  example: 50000
                  description: 服务器内部错误
                message:
                  type: string
                  example: "<error_message>"
                  description: 在尝试执行用户授权流程时出现错误
          50001:
            description: |
              由于网络问题导致认证失败，通常由于代理问题导致服务器无法正常发送请求到discord等海外服务
            schema:
              type: object
              properties:
                code:
                  type: integer
                  example: 40007
                  description: 网络连接问题
                message:
                  type: string
                  example: "<error_message>"
                  description: 网络连接问题
        """
    result = auth_service.auth_code_authenticate()
    return jsonify(result.to_dict())


@inject
@auth_bp.route('/validate', methods=['POST'])
def access_token_authenticate(auth_service: AuthService) -> Response:
    """
        用户access token登录验证接口
        ---
        tags:
          - 认证接口
        description: |
          使用access token直接进行登录校验，不会更改后端数据状态，准确的说，去除了原先双refresh token的设定来简化认证逻辑，避免一些
          繁琐复杂的重复校验，采用透明化的access token刷新策略
          也正因为如此，这个接口会导致数据库变更，采用POST方法
        parameters:
          - name: access_token
            in: header
            required: true
            description: musicatri授权码，在经过discord授权后获取
            type: string
            example: "<access_token>"
          - name: device_id
            in: header
            required: true
            description: 设备id号，由前端生成后在授权时发送，用于标识统一用户不同设备
            type: string
            example: "<device_id>"
          - name: Accept-Language
            in: header
            required: false
            description: 指定后端响应使用的本地化语言
            type: string
            example: "en-US"
        responses:
          20000:
            description: 用户授权成功
            schema:
              type: object
              properties:
                code:
                  type: int
                  example: 20000
                  description: 响应状态码
                message:
                  type: string
                  example: "<success_message>"
                  description: 用户登录成功之后的响应消息
          40001:
            description: |
              非法参数提交，通常是由于没有遵循给定的参数提交格式，认证接口仅接受access_token作为参数提交
            schema:
              type: object
              properties:
                code:
                  type: integer
                  example: 40001
                  description: 参数非法
                message:
                  type: string
                  example: "<error_message>"
                  description: 参数异常
          40003:
            description: |
              权限拒绝，用户在未登录，或是状态已经封禁的情况下无法调用此接口
            schema:
              type: object
              properties:
                code:
                  type: integer
                  example: 40003
                  description: 权限拒绝
                message:
                  type: string
                  example: "<error_message>"
                  description: 拒绝登入
          40004:
            description: |
              用户提交的access token已经过期，前端接收到这个响应码之后应该执行refresh token逻辑，使用
              refresh token尝试刷新access token
            schema:
              type: object
              properties:
                code:
                  type: integer
                  example: 40004
                  description: access token过期
                message:
                  type: string
                  example: "<error_message>"
                  description: token过期
          40005:
            description: |
              提交的token为非法token，通常由于payload错误，或者是app secret错误，前端同样应该尝试使用
              refresh token刷新获取access token
            schema:
              type: object
              properties:
                code:
                  type: integer
                  example: 40005
                  description: 非法token
                message:
                  type: string
                  example: "<error_message>"
                  description: 非法token
          40006:
            description: |
              用户会话已经被关闭，这意味着access token以及refresh token已经失效，前端在接受到
              此响应码之后应当直接执行discord auth code认证工作流
            schema:
              type: object
              properties:
                code:
                  type: integer
                  example: 40006
                  description: token会话已经被关闭
                message:
                  type: string
                  example: "<error_message>"
                  description: 会话被关闭
          40400:
            description: |
              用户不存在
            schema:
              type: object
              properties:
                code:
                  type: integer
                  example: 40400
                  description: 用户不存在
                message:
                  type: string
                  example: "<error_message>"
                  description: 用户不存在
          50000:
            description: |
              服务器内部错误导致无法正常执行授权流程，出错的原因可能为数据库连接、discord请求超时等
            schema:
              type: object
              properties:
                code:
                  type: integer
                  example: 50000
                  description: 服务器内部错误
                message:
                  type: string
                  example: "<error_message>"
                  description: 在尝试执行用户授权流程时出现错误
          50001:
            description: |
              由于网络问题导致认证失败，通常由于代理问题导致服务器无法正常发送请求到discord等海外服务
            schema:
              type: object
              properties:
                code:
                  type: integer
                  example: 40007
                  description: 网络连接问题
                message:
                  type: string
                  example: "<error_message>"
                  description: 网络连接问题
        """
    result = auth_service.access_token_authenticate()
    return jsonify(result.to_dict())


