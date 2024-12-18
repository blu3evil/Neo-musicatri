""" 亚托莉相关接口 """
from flask import Blueprint
from services.atri_service import atri_service

atri_bp_v1 = Blueprint('atri_bp_v1', __name__, url_prefix='/api_server/v1/atri')

@atri_bp_v1.route('/start', methods=['POST'])
def start_atri():
    """
    启动亚托莉接口
    ---
    tags:
      - 机器人接口
    description: 用于启动亚托莉机器人
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
      - 机器人接口
    description: 用于停止亚托莉机器人
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
      - 机器人接口
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