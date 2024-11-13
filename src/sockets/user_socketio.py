"""
用户端socketio
"""
from utils import log
from flask import request
from flask_socketio.namespace import Namespace

class UserSocketIO(Namespace):
    @staticmethod
    def on_connect():
        """
        用户连接到UserSocketIO，执行登录校验逻辑
        """
        log.info(request.sid)

    @staticmethod
    def acknowledgment():
        """ 确认客户端接收回调 """
        print('message was received!')

    @staticmethod
    def on_message():
        """ 客户端发送消息 """
        print('received message: ' + data)

    @staticmethod
    def on_json(json):
        """ 客户端发送json消息 """
        print('received json: ' + str(json))

    @staticmethod
    def on_disconnect():
        """ 客户端中断websocket连接"""
        print('Client disconnected')