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