""" 亚托莉相关接口 """
from flask import Blueprint, jsonify, request

from bot_server.services.atri_service import atri_service
from bot_server.bot_server_context import context

atri_bp_v1 = Blueprint('atri_bp_v1', __name__, url_prefix='/api/v1/bot/atri')
locale = context.locale
@atri_bp_v1.route('/initialize', methods=['POST'])
def initialize_atri():
  """
  初始化亚托莉接口
  ---
  tags:
    - 机器人接口
  description: 用于初始化机器人线程
  responses:
    200:
      description: 机器人初始化成功
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
  result = atri_service.initialize_atri()
  return result.as_response()

@atri_bp_v1.route('/terminate', methods=['POST'])
def terminate_atri():
    """
    启动亚托莉接口
    ---
    tags:
      - 机器人接口
    description: 用于停止机器人线程
    responses:
      200:
        description: 机器人启动成功
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

@atri_bp_v1.route('/play', methods=['POST'])
def atri_play():
    """
    亚托莉音乐播放接口
    ---
    tags:
      - 机器人接口
    description: 音乐播放
    parameters:
      - name: songid
        in: body
        required: true
        schema:
          type: object
          properties:
            songid:
              type: string
              description: 歌曲的uuid
              example: '16541audc-jssd18421-asc115'
    responses:
      200:
        description: 成功播放
        schema:
          type: object
          properties:
            message:
              type: string
              examples: 'playing {id} ...'
      403:
        description: 播放失败
        schema:
          type: object
          properties:
            message:
              type: string
              examples: 'error at playing'
    """
    _ = locale.get()
    code = request.get_json().get('songid')
    if not code: return jsonify({ 'message': _('invalid argument') }), 403  # 参数错误
    result = atri_service.playsongbyid(code)
    return result.as_response()
# @atri_bp_v1.route('/test/<message>', methods=['GET'])
# def atri_test(message):
#     from sockets.event_dispatcher import admin_socket_dispatcher
#     admin_socket_dispatcher.emit('test', message)
#     return jsonify({'message': 'ok'}), 200