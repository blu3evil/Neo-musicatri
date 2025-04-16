"""
用户端socketio
"""
from flask_socketio import SocketIO, disconnect, emit

from flask import request
from server_auth.context import context
from server_auth.services import auth_service
from events import SocketioEvent

session_sid_name = 'admin_sid'

session = context.session
logger = context.logger

# 初始化用户长连接
def init(socketio: SocketIO):
    # noinspection PyUnresolvedReferences
    @socketio.on('connect', namespace='/socket/admin')
    def admin_connect():
        """ 用户连接到UserSocketIO，执行登录校验逻辑 """
        user_id = session.get('user_id')
        result = auth_service.verify_login(user_id)  # 校验用户当前登入状态
        if result.code != 200:
            emit(SocketioEvent.CONNECT_REJECT, result.as_dict())
            disconnect()  # 在用户没有权限的时候断开连接
            return

        result = auth_service.verify_role(user_id, 'admin')  # 校验管理员权限
        if result.code != 200:
            emit(SocketioEvent.CONNECT_REJECT, result.as_dict())
            disconnect()
            return

        session[session_sid_name] = str(request.sid)  # 记录用户sid
        logger.info(f'admin socket connected, admin sid: {session.get(session_sid_name)}')
        emit(SocketioEvent.CONNECT_ACCEPT, result.as_dict())


    @socketio.on('disconnect', namespace='/socket/admin')
    def admin_disconnect():
        """ 客户端中断websocket连接 """
        logger.info(f'admin socket disconnected, admin sid: {session.get(session_sid_name)}')
        session.pop(session_sid_name, None)  # 清除sid
