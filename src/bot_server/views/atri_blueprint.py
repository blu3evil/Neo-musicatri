""" 亚托莉相关接口 """
from flask import Blueprint

from bot_server.services.atri_service import atri_service

atri_bp_v1 = Blueprint('atri_bp_v1', __name__, url_prefix='/api/v1/admin/bot/atri')

@atri_bp_v1.route('/launch', methods=['POST'])
def launch_atri():
    """
    启动亚托莉线程机器人接口
    ---
    tags:
      - 亚托莉机器人接口
    description: 在机器人连接服务之前，启动机器人线程
    responses:
      200:
        description: 亚托莉机器人线程启动成功
        schema:
          type: object
          properties:
            message:
              type: string
              examples: 'bot thread start successfully'
      400:
        description: 不支持的操作
        schema:
          type: object
          properties:
            message:
              type: string
              examples: 'unsupported operation'
              description: '操作不支持'
    """
    result = atri_service.launch_atri()
    return result.as_response()

@atri_bp_v1.route('/terminate', methods=['POST'])
def terminate_atri():
    """
    终止亚托莉机器人线程接口
    ---
    tags:
      - 亚托莉机器人接口
    description: 用于停止亚托莉机器人线程
    responses:
      200:
        description: 成功停止机器人线程
        schema:
          type: object
          properties:
            message:
              type: string
              examples: 'start success'
      400:
        description: 不支持的操作
        schema:
          type: object
          properties:
            message:
              type: string
              examples: 'unsupported operation'
              description: '操作不支持'
    """
    result = atri_service.terminate_atri()
    return result.as_response()

@atri_bp_v1.route('/start', methods=['POST'])
def start_atri():
    """
    启动亚托莉机器人接口
    ---
    tags:
      - 亚托莉机器人接口
    description: 在线程启动之后，使用此接口启动亚托莉机器人
    responses:
      200:
        description: 机器人启动成功
        schema:
          type: object
          properties:
            message:
              type: string
              examples: 'start success'
    """
    result = atri_service.start_atri()
    return result.as_response()

@atri_bp_v1.route('/stop', methods=['POST'])
def stop_atri():
    """
    停止亚托莉接口
    ---
    tags:
      - 亚托莉机器人接口
    description: 在亚托莉机器人运行的前提下，使用此接口停止机器人
    responses:
      200:
        description: 机器人停止成功
        schema:
          type: object
          properties:
            message:
              type: string
              examples: 'start success'
    """
    result = atri_service.stop_atri()
    return result.as_response()

@atri_bp_v1.route('/status', methods=['GET'])
def atri_status():
    """
    亚托莉状态接口
    ---
    tags:
      - 亚托莉机器人接口
    description: 获取当前亚托莉状态
    responses:
      200:
        description: 成功获取机器人状态
        schema:
          type: object
          properties:
            message:
              type: string
              examples: 'start success'
            data:
             type: object
             properties:
               status:
                 type: string
                 examples: 'stopped'
                 description: 机器人当前属于未启动状态
    """
    result = atri_service.get_atri_status()
    return result.as_response()

# @atri_bp_v1.route('/test/<message>', methods=['GET'])
# def atri_test(message):
#     from sockets.event_dispatcher import admin_socket_dispatcher
#     admin_socket_dispatcher.emit('test', message)
#     return jsonify({'message': 'ok'}), 200