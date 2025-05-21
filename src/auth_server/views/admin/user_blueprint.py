""" 管理员用户接口 """
from flask import Blueprint, request

from auth_server.services.auth_service import user_auth_service_v2
from auth_server.services.user_service import user_service_v1
from auth_server.context import context

admin_user_bp_v1 = Blueprint('admin_user_bp_v1', __name__, url_prefix='/api/v1/admin/users')
session = context.session
logger = context.logger
locale = context.locale
aspect = context.aspect

# @auth_service_v1.login_required
# @auth_service_v1.role_required('admin')
@admin_user_bp_v1.route('/preview/all', methods=['GET'])
@user_auth_service_v2.validate_required(['user', 'admin'])
def get_all_users_preview():
    """
    用户概览获取接口
    ---
    tags:
      - 管理员接口
    description: 管理端获取用户列表，此接口仅仅返回概览数据而非详情数据
    produces:
      - application/json
    parameters:
      - in: query
        name: username
        required: false
        description: 对标识名进行查询
        schema:
          type: string
        example: "pinecloneee"
      - in: query
        name: global_name
        required: false
        schema:
          type: string
        description: 对用户名进行查询
        example: "pineclone"
      - in: query
        name: is_active
        required: false
        schema:
          type: integer
        description: 对状态进行查询，-1表示任意、0表示激活、1表示禁用
        example: 0
    responses:
      200:
        description: 成功获取用户列表
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
                example: 1285865537603371029
                description: 用户id，这里是discord用户id
              username:
                type: string
                example: "pinecloneee"
                description: 标识名，在discord中此名称不可重复
              global_name:
                type: string
                example: "pineclone"
                description: 用户名，用于显示
              roles:
                type: array
                items:
                  type: string
                  example: ['admin', 'user']
                  description: 用户当前的权限级别
              is_active:
                type: boolean
                example: true
                description: 当前用户状态
    """
    args = request.args
    condition = {
        'username': args.get('username', type=str),
        'global_name': args.get('global_name', type=str),
        'is_active': args.get('is_active', type=int)
    }
    result = user_service_v1.get_all_users_preview(condition)
    return result.as_response()

# @auth_service_v1.login_required
# @auth_service_v1.role_required('admin')
@admin_user_bp_v1.route('/preview', methods=['GET'])
@user_auth_service_v2.validate_required(['user', 'admin'])
@aspect.pagination_query()  # 分页
def get_users_preview(current_page, page_size):
    """
    用户概览获取接口
    ---
    tags:
      - 管理员接口
    description: 管理端获取用户列表，此接口仅仅返回概览数据而非详情数据
    produces:
      - application/json
    parameters:
      - in: query
        name: username
        required: false
        description: 对标识名进行查询
        schema:
          type: string
        example: "pinecloneee"
      - in: query
        name: global_name
        required: false
        schema:
          type: string
        description: 对用户名进行查询
        example: "pineclone"
      - in: query
        name: is_active
        required: false
        schema:
          type: integer
        description: 对状态进行查询，-1表示任意、0表示激活、1表示禁用
        example: 0
      - in: query
        name: currentPage
        required: true
        schema:
          type: integer
        description: 当前所在页码，基于此推算查询偏移值
        example: 1
      - in: query
        name: pageSize
        required: true
        schema:
          type: integer
        description: 查询结果每页显示多少条数据，基于此推算查询偏移值
        example: 10
    responses:
      200:
        description: 成功获取用户列表
        schema:
          type: object
          properties:
            total:
              type: integer
              description: 共存在多少条数据
              example: 100
            users:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                    example: 1285865537603371029
                    description: 用户id，这里是discord用户id
                  username:
                    type: string
                    example: "pinecloneee"
                    description: 标识名，在discord中此名称不可重复
                  global_name:
                    type: string
                    example: "pineclone"
                    description: 用户名，用于显示
                  roles:
                    type: array
                    items:
                      type: string
                      example: ['admin', 'user']
                      description: 用户当前的权限级别
                  is_active:
                    type: boolean
                    example: true
                    description: 当前用户状态
    """
    args = request.args
    condition = {
        'username': args.get('username', type=str),
        'global_name': args.get('global_name', type=str),
        'is_active': args.get('is_active', type=int)
    }
    result = user_service_v1.get_users_preview(condition, current_page, page_size)
    return result.as_response()

# @auth_service_v1.login_required
# @auth_service_v1.role_required('admin')
@admin_user_bp_v1.route('<int:user_id>/details', methods=['GET'])
@user_auth_service_v2.validate_required(['user', 'admin'])
def get_user_details(user_id):
    """
    获取指定用户的详细信息
    ---
    tags:
      - 管理员接口
    description: 根据id获取指定用户的信息
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: 获取详情的目标用户id
    responses:
      200:
        description: 成功获取用户详情
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                accent_color:
                  type: integer
                  example: null
                  description: 用户自定义的个人资料卡片主题颜色，null代表用户未设置此颜色
                avatar:
                  type: string
                  example: "fe79f3019287ae2a3658cf6c5e3231e5"
                  description: 用户头像哈希值，可以通过discord头像URL拼接后请求获取用户头像
                avatar_decoration_data:
                  type: null
                  example: null
                  description: 预留字段，头像框装饰效果
                banner:
                  type: string
                  example: null
                  description: 用户的个人资料横幅图像的哈希值，null代表未设置横幅
                banner_color:
                  type: string
                  example: "#7289DA"
                  description: 用户个人资料卡的横幅背景颜色，null代表用户未设置
                clan:
                  type: string
                  example: null
                  description: 预留字段
                discriminator:
                  type: string
                  example: "0"
                  description: 用户标识符，用于区别拥有相同用户名的用户
                flags:
                  type: integer
                  example: 0
                  description: 用户帐户的标志位，表示用户的某些属性
                global_name:
                  type: string
                  example: "pinecloneee"
                  description: 用户的全局用户名，Discord账户的唯一标识
                id:
                  type: string
                  example: "1285865537603371029"
                  description: 64位雪花ID，用户的唯一标识符（ID）
                is_active:
                  type: boolean
                  example: true
                  description: 表示用户是否活跃
                locale:
                  type: string
                  example: "zh-CN"
                  description: 用户的语言和地区设置，表示用户的Discord界面语言
                mfa_enabled:
                  type: boolean
                  example: true
                  description: 用户是否启用了多因素认证（MFA/2FA）
                premium_type:
                  type: integer
                  example: 0
                  description: 表示用户的Discord Nitro类型，0表示无Nitro，1表示标准Nitro，2表示正式Nitro
                premium_type:
                  type: integer
                  example: 0
                  description: 用户公共帐户的标志位，与flags类似，但表示用户在公众场合显示的标志
                roles:
                  type: array
                  example: ['admin', 'user']
                  description: 表示用户当前拥有的musicatri权限
            message:
              type: string
              example: "hit cache"
              description: 描述请求是否命中缓存
      404:
        description: 用户不存在
      403:
        description: 权限不足，我发请求此接口
    """
    result = user_service_v1.get_user_details(user_id)
    return result.as_response()

# @auth_service_v1.login_required
# @auth_service_v1.role_required('admin')
@admin_user_bp_v1.route('roles', methods=['GET'])
@user_auth_service_v2.validate_required(['user', 'admin'])
def get_all_roles():
    """
    获取所有权限级别
    ---
    tags:
      - 管理员接口
    description: 获取所有可用的权限级别，名称以及id
    responses:
      200:
        description: 成功获取权限级别列表
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                    example: 1
                    description: 权限级别的id
                  name:
                    type: string
                    example: user
                    description: 权限级别名称
                  description:
                    type: string
                    example: Normal user role
                    description: 对权限级别的描述
                  disabled:
                    type: boolean
                    example: false
                    description: 此属性用于描述某个权限等级是否能被添加到用户，或是从用户身上移除
    """
    result = user_service_v1.get_all_roles()
    return result.as_response()

# @auth_service_v1.login_required
# @auth_service_v1.role_required('admin')
@admin_user_bp_v1.route('/<int:user_id>', methods=['PATCH'])
@user_auth_service_v2.validate_required(['user', 'admin'])
def patch_user(user_id):
    """
    增量更新用户数据
    ---
    tags:
      - 管理员接口
    description: 对用户数据进行增量更新
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: 执行此次增量更新的目标用户id
      - name: data
        in: body
        type: object
        properties:
          is_active:
            type: boolean
            example: true
            description: 更新用户账户的状态
          roles:
            type: array
            example: ['admin', 'user']
            description: 更新用户账户权限级别
    responses:
      200:
        description: 成功更新用户数据
        schema:
          type: object
          properties:
            message:
              type: string
              example: "user updated successfully"
              description: 用户账户信息更新成功
    """
    body = request.get_json()
    data = {
        'is_active': body.get('is_active'),
        'roles': body.get('roles')
    }
    result = user_service_v1.update_user(user_id, data)
    return result.as_response()

# @auth_service_v1.login_required
# @auth_service_v1.role_required('admin')
@admin_user_bp_v1.route('<int:user_id>', methods=['DELETE'])
@user_auth_service_v2.validate_required(['user', 'admin'])
def delete_user(user_id):
    """
    删除用户
    ---
    tags:
      - 管理员接口
    description: 删除指定用户，删除用户的同时会清理用户的会话信息
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: 删除目标用户的id
    responses:
      200:
        description: 成功删除用户
        schema:
          type: object
          properties:
            message:
              type: string
              example: "user deleted successfully"
              description: 成功删除用户
    """
    result = user_service_v1.delete_user(user_id)
    return result.as_response()
