"""
系统级别API接口
"""
from datetime import time, datetime

from auth_server.services.auth_service import user_auth_service_v2
from flask import Blueprint, jsonify
import time, math
from auth_server.context import context
from common.utils.context import ResourceContextConfigKey

status_bp_v1 = Blueprint('status_bp_v1', __name__, url_prefix='/api/v1/system')
start_time = time.time()
created_at = int(datetime.now().timestamp())

cache = context.cache
config = context.config

@status_bp_v1.route('/health', methods=['GET'])
def health():
    """
    健康检查接口
    ---
    tags:
      - 系统接口
    description: 用于前端或者docker执行健康检查
    responses:
      200:
        description: 服务处于健康状态
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                uptime:
                  type: integer
                  example: 300
                  description: 服务器存活时间，单位为"秒"
                created_at:
                  type: integer
                  example: 1731094767
                  description: 服务器上线时间，使用时间戳
    """
    current_time = time.time()
    uptime = math.floor(current_time - start_time)
    return jsonify({
        'data': {
            'uptime': uptime,
            'created_at': created_at,
        }
    })


# @auth_service_v1.login_required
# @auth_service_v1.role_required('user')
@status_bp_v1.route('/info', methods=['GET'])
@cache.cached(timeout=60)
@user_auth_service_v2.validate_required()
def info():
    """
    服务器描述接口
    ---
    tags:
      - 系统接口
    description: 用于查询服务基本信息
    responses:
      200:
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                name:
                  type: string
                  example: "musicatri"
                  description: 服务名称
                version:
                  type: string
                  example: "1.0.0"
                  description: 服务版本号
                description:
                  type: string
                  example: "neo-musicatri"
                  description: 服务描述信息
    """
    return jsonify({
        'data': {
            'name': config.get(ResourceContextConfigKey.INFO_NAME),
            'version': config.get(ResourceContextConfigKey.INFO_VERSION),
            'description': config.get(ResourceContextConfigKey.INFO_DESCRIPTION),
        }
    })  # 成功获取服务器数据