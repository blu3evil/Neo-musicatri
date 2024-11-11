from flask import Flask
from flask_socketio import SocketIO
from utils.config_old import default_config, DefaultConfigTag


def socketio_configure(app: Flask):
    secret_key = default_config.get(DefaultConfigTag.APP_SECRET_KEY)
    app.config['SECRET_KEY'] = secret_key
    socketio = SocketIO()  # socketio
    socketio.init_app(app=app, cors_allowed_origins='*')
    # 注册亚托莉socket
    musicatri_user_socketio_registry(socketio)

# atri socketio
def musicatri_user_socketio_registry(socketio: SocketIO):
    """
    亚托莉用户端socketio注册
    :param socketio: 项目socketio实例
    """
    def acknowledgment():
        """ 确认客户端接收回调 """
        print('message was received!')

    @socketio.on('message')
    def handle_message(data):
        """ 客户端发送消息 """
        print('received message: ' + data)

    @socketio.on('json')
    def handle_json(json):
        """ 客户端发送json消息 """
        print('received json: ' + str(json))

    @socketio.on('disconnect')
    def handle_disconnect():
        """ 客户端中断websocket连接"""
        print('Client disconnected')