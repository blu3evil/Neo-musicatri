"""
系统级别API接口
"""
from flask import Blueprint, jsonify
from injector import inject

from service.abs.system_service import SystemService

system_bp = Blueprint('system_bp', __name__, url_prefix='/api/system')

@inject
@system_bp.route('/health', methods=['GET'])
def status(system_service: SystemService):
    """
    健康检查接口
    ---
    tags:
      - 系统接口
    description: |
      因为可能需要执行容器的健康检查，设计了这个端口，可以用作健康检查接口，或者查询一些服务的基本情况，例如版本信息、
      上线时间等
    responses:
      20000:
        description: Musicatri服务器后端处于健康状态
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 20000
              description: 服务器正常对外提供响应
            message:
              type: string
              example: "health"
              description: 当前状态标记为health
            data:
              type: object
              properties:
                version:
                  type: string
                  example: "1.0.0"
                  description: Musicatri服务端版本
                uptime:
                  type: integer
                  example: 10
                  description: Musicatri服务上线时长
      50000:
        description: Musicatri服务器后端处于亚健康状态
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 50000
              description: 服务器内部错误
            message:
              type: string
              example: "unhealthy"
              description: 服务器健康状态标记为unhealthy
    """
    result = system_service.status()
    return jsonify(result.to_dict())


@inject
@system_bp.route("/config", methods=['GET'])
def config(system_service: SystemService):
    """
    Musicatri当前配置参数检视接口
    ---
    tags:
      - 系统接口
    description: |
      可以在项目调试阶段或者上线之后用于获取项目的配置信息，在DEV_MODE配置参数为False的时候会对项目敏感参数进行脱敏处理
    responses:
      20000:
        description: 拉取后端配置数据成功
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 20000
              description: 服务器正常对外提供响应
            message:
              type: string
              example: "operation success"
              description: 接口响应成功，状态正常
            data:
              type: object
              properties:
                APP_SECRET_KEY:
                  type: string
                  example: musicatri
                  description: Musicatri后端服务api密钥
                CONSOLE_LOG_LEVEL:
                  type: string
                  example: INFO
                  description: 控制台输出日志级别
                DISCORD_BOT_ACTIVITY:
                  type: int
                  example: 2
                  description: Discord机器人当前状态码值
                MORE_CONFIG_TAG:
                  type: string
                  example: ...
                  description: 以及更多可能的配置项
      50000:
        description: 服务器后端错误
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 50000
              description: 服务器内部错误
            message:
              type: string
              example: "server internal error"
              description: 服务器无法正常响应请求
    """
    # 此接口上线后需要做好权限校验避免滥用
    result = system_service.config()
    return jsonify(result.to_dict())
