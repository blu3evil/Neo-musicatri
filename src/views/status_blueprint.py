"""
系统级别API接口
"""
from datetime import time, datetime

from flask import Blueprint, jsonify
from utils import config, ConfigEnum, auth
import time, math
from utils.middlewares import cache

status_bp_v1 = Blueprint('status_bp_v1', __name__, url_prefix='/api/v1/status')
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
        'uptime': uptime,
        'created_at': created_at,
    }), 200


@status_bp_v1.route('/info', methods=['GET'])
@auth.login_required
@cache.cached(timeout=60)
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
    name = config.get(ConfigEnum.APP_INFO_NAME)
    version = config.get(ConfigEnum.APP_INFO_VERSION)
    description = config.get(ConfigEnum.APP_INFO_DESCRIPTION)
    return jsonify({
        'name': name,
        'version': version,
        'description': description,
    }), 200