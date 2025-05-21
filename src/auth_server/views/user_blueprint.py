""" 用户接口 """
from flask import Blueprint

from auth_server.services.auth_service import user_auth_service_v2
from auth_server.services.user_service import user_service_v1
from auth_server.context import context

user_bp_v1 = Blueprint('user_bp_v1', __name__, url_prefix='/api/v1/users')
session = context.session
locale = context.locale

# @auth_service_v1.login_required
@user_bp_v1.route('/me/details', methods=['GET'])
@user_auth_service_v2.validate_required()
def get_current_user_details(current_user):
    """
    当前用户详情信息查询
    ---
    tags:
      - 用户接口
    description: 用于用户在登录之后查询自身详情数据使用
    responses:
      200:
        description: 成功查询用户数据
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
      401:
        description: 用户未登录
      403:
        description: 用户权限不足
      404:
        description: 用户不存在
    """
    # user_id = session.get('user_id')
    user_id = current_user.get('user_id')
    result = user_service_v1.get_user_details(user_id)
    return result.as_response()  # 将结果作为响应



