"""
用户端socketio
"""
from flask_socketio import SocketIO, disconnect, emit

from utils import log, locales
from flask import request
from core import session
from services.auth_service import auth_service
from sockets.events import ServerEvent

session_sid_name = 'user_sid'

# 初始化用户长连接
def init(socketio: SocketIO):
    # noinspection PyUnresolvedReferences
    @socketio.on('connect', namespace='/socket/user')
    def user_connect():
        """ 用户连接到UserSocketIO，执行登录校验逻辑 """
        user_id = session.get('user_id')
        result = auth_service.verify_login(user_id)  # 校验用户当前登入状态
        if result.code != 200:
            emit(ServerEvent.CONNECT_REJECT, result.as_dict())
            disconnect()  # 在用户没有权限的时候断开连接
        else:
            session[session_sid_name] = str(request.sid)  # 记录用户sid
            log.info(f'user socket connected, user sid: {session.get(session_sid_name)}')
            emit(ServerEvent.CONNECT_ACCEPT, result.as_dict())

    @socketio.on('message', namespace='/socket/user')
    def receive_user_message(data):
        """ 客户端发送消息 """
        _ = locales.get()
        print(f'received message: {data}')

    @socketio.on('disconnect', namespace='/socket/user')
    def user_disconnect():
        """ 客户端中断websocket连接"""
        log.info(f'user socket disconnected, user sid: {session.get(session_sid_name)}')
        session.pop(session_sid_name, None)  # 清除sid

