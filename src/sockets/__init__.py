from flask_socketio import SocketIO

socketio = SocketIO()  # 初始化flask_io

# 注册socketio路由
from sockets.user_socketio import UserSocketIO
socketio.on_namespace(UserSocketIO("/user/home"))  # 用户家目录socketio