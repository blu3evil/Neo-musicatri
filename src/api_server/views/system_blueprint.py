"""
系统级别API接口
"""
from datetime import time, datetime

from api_server.services.auth_service import auth_service
from flask import Blueprint, jsonify
import time, math
from api_server.app_context import cache, config, ConfigKey

status_bp_v1 = Blueprint('status_bp_v1', __name__, url_prefix='/api/v1/system')
start_time = time.time()
created_at = int(datetime.now().timestamp())

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


@status_bp_v1.route('/info', methods=['GET'])
@cache.cached(timeout=60)
@auth_service.require_login
@auth_service.require_role('user')
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
            'name': config.get(ConfigKey.APP_INFO_NAME),
            'version': config.get(ConfigKey.APP_INFO_VERSION),
            'description': config.get(ConfigKey.APP_INFO_DESCRIPTION),
        }
    })  # 成功获取服务器数据