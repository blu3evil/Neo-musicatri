# 服务端事件
class SocketioEvent:
    # 用户事件
    CONNECT_REJECT = 'socketio:connect:reject'
    CONNECT_ACCEPT = 'socketio:connect:accept'

    ATRI_STATE_CHANGE = 'socketio:atri:state:change'  # 亚托莉状态变更

# 亚托莉事件
class AtriEvent:
    CONNECT = 'atri:connect:success'
    CONNECT_FAILED = 'atri:connect:failed'  # 连接失败
    DISCONNECT = 'atri:disconnect:success'
    DISCONNECT_FAILED = 'atri:disconnect:failed',
    RECONNECT = 'atri:reconnect',
    CLOSE = 'atri:close',  # 机器人被关闭
    READY = 'atri:ready',  # 机器热就绪
    STATE_CHANGE = 'atri:state:change'
