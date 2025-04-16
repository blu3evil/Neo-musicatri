# 服务端事件
class SocketioEvent:
    # 用户事件
    CONNECT_REJECT = 'socketio:connect:reject'
    CONNECT_ACCEPT = 'socketio:connect:accept'

    ATRI_STATE_CHANGE = 'socketio:atri:state:change'  # 亚托莉状态变更

class BotEvent:
    CONNECT_SUCCESS = 'bot:connect:success'
    CONNECT_FAILED = 'bot:connect:failed'  # 连接失败
    DISCONNECT_SUCCESS = 'bot:disconnect:success'
    DISCONNECT_FAILED = 'bot:disconnect:failed',
    RECONNECT = 'atri:reconnect',  # 重连事件
    CLOSE = 'bot:close',  # 机器人被关闭
    READY = 'bot:ready',  # 机器热就绪
    STATE_CHANGE = 'bot:state:change'  # 机器人状态变更


