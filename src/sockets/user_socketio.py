"""
用户端socketio
"""
from flask_socketio import SocketIO, disconnect, emit

from utils import log, locales
from flask import request
from core import session
from services.auth_service import auth_service
from sockets.events import Events


# 初始化用户长连接
def init(socketio: SocketIO):
    # noinspection PyUnresolvedReferences
    @socketio.on('connect', namespace='/socket/user')
    def user_connect():
        """ 用户连接到UserSocketIO，执行登录校验逻辑 """
        _ = locales.get()
        result = auth_service.verify_login()  # 校验用户当前登入状态
        log.debug(result)
        if result.code != 200:
            emit(Events.CONNECT_ERROR, result.as_dict())
            disconnect()  # 在用户没有权限的时候断开连接
        else:
            session['sid'] = str(request.sid)  # 记录用户sid
            log.debug(session.get('sid'))
            emit(Events.CONNECT_SUCCESS, result.as_dict())


    @socketio.on('message', namespace='/socket/user')
    def receive_user_message():
        """ 客户端发送消息 """
        print('received message: ')

    @socketio.on('disconnect', namespace='/socket/user')
    def user_disconnect():
        """ 客户端中断websocket连接"""
        session.pop('sid', None)  # 清除sid
        print('Client disconnected')


