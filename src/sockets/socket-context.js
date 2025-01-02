// noinspection JSUnresolvedReference

import mitt from 'mitt'
import { AbstractState, StateContext } from '@/pattern.js'
import { io } from 'socket.io-client'
import { Result } from '@/common.js'
import { Events } from '@/events.js'
import { i18n } from '@/locale/index.js'

class SocketState extends AbstractState {
  async connect(context) {
    return new Result(400, 'unsupported operation')
  }
  async disconnect(context) {
    return new Result(400, 'unsupported operation')
  }

  enter(context) {  // 状态变更
    context.eventbus.emit(Events.MITT.SOCKET_CONTEXT.STATE.CHANGE, this.getIdentify())
  }
}

// 已连接
class ConnectedState extends SocketState {
  getIdentify() {
    return 'connected'
  }

  enter(context) {
    super.enter(context)  // 触发事件
    context.socket.once('disconnect', () => {
      context.setState(new DisconnectedState()) // 切换到未连接状态
      context.eventbus.emit(Events.MITT.SOCKET_CONTEXT.DISCONNECT.FORCE)  // 触发强制断开事件
    })
  }

  async connect(context) {
    return new Result(200, 'already connected')
  }

  disconnect(context) {
    context.setState(new DisconnectingState()) // 正在断开连接状态
    return new Promise((resolve) => {
      let timeoutId = 0
      timeoutId = setTimeout(() => {  // 断开连接超时
        context.eventbus.emit(
          Events.MITT.SOCKET_CONTEXT.DISCONNECT.FAILED,
          i18n.global.t('sockets.socket-context.timeout')
        )
        context.setState(new ConnectedState())  // 恢复状态
        resolve(new Result(601))
      }, context.timeout)

      context.socket.off('disconnect') // 清除原始断开连接事件
      context.socket.once('disconnect', () => {
        clearTimeout(timeoutId) // 清除超时事件
        context.setState(new InitializingState())  // 重新初始化socketio实例
        context.eventbus.emit(Events.MITT.SOCKET_CONTEXT.DISCONNECT.SUCCESS)
        resolve(new Result(200, 'disconnect success'))
      })
      context.socket.disconnect()
    })
  }
}

// 正在连接
class ConnectingState extends SocketState {
  getIdentify() {
    return 'connecting'
  }
}

// 正在断开连接
class DisconnectingState extends SocketState {
  getIdentify() {
    return 'disconnecting'
  }
}

// 初始化状态
class InitializingState extends AbstractState {
  getIdentify() {
    return 'initializing'
  }

  enter(context) {
    super.enter(context)
    console.log(`init socket for url: ${context.url}`)

    // todo: 此处需要重新挂载事件，不能仅仅初始化socket

    context.socket = io(context.url, {  // 初始化socketio
      autoConnect: false,  // 禁用自动连接
      reconnection: false,
      transports: ['websocket', 'polling'], // 使用websocket而不是轮询
    })
    context.setState(new DisconnectedState())  // 切换到未连接状态
  }
}

// 未连接状态
class DisconnectedState extends SocketState {
  getIdentify() {
    return 'disconnected'
  }

  fadeout(context) {  // 清理资源
    context.off(Events.SOCKETIO.CONNECT.REJECT)
    context.off(Events.SOCKETIO.CONNECT.ACCEPT)
  }

  async disconnect(context) {
    return new Result(200, 'already disconnected')
  }

  connect(context) {
    context.setState(new ConnectingState()) // 正在连接状态
    return new Promise((resolve) => {
      let timeoutId = 0
      timeoutId = setTimeout(() => {  // 连接超时
        context.eventbus.emit(
          Events.MITT.SOCKET_CONTEXT.CONNECT.FAILED,
          i18n.global.t('sockets.socket-context.timeout'),
        )
        context.setState(new DisconnectedState()) // 切换到未连接状态
        resolve(new Result(601))
      }, context.timeout)

      // 连接socketio
      context.socket.connect()

      // 服务端拒绝连接
      context.socket.once(Events.SOCKETIO.CONNECT.REJECT, response => {
        clearTimeout(timeoutId)  // 清理超时
        context.setState(new InitializingState())  // 重新初始化socketio实例
        let result = Result.fromJSON(response)
        context.eventbus.emit(
          Events.MITT.SOCKET_CONTEXT.CONNECT.FAILED,
          result.message,
        )
        resolve(result)
      })

      // 连接建立成功
      context.socket.once(Events.SOCKETIO.CONNECT.ACCEPT, async response => {
        clearTimeout(timeoutId) // 清理超时
        context.setState(new ConnectedState()) // 切换到已连接状态
        context.eventbus.emit(Events.MITT.SOCKET_CONTEXT.CONNECT.SUCCESS)
        resolve(Result.fromJSON(response))
      })
    })
  }
}

export class SocketContext extends StateContext {
  constructor(url, timeout=5000) {
    super()
    this.url = url
    this.timeout = timeout
    this.eventbus = mitt()
    this.setState(new InitializingState())
    this.preInitialize()  // 执行预初始化
  }

  preInitialize() {}  // 预初始化

  on(event, listener) {  // 挂载事件
    this.socket.on(event, listener)
  }

  once(event, listener) {  // 挂载单次事件
    this.socket.once(event, listener)
  }

  off(event) {  // 卸载事件
    this.socket.off(event)
  }

  emit(event, callback) {  // 发布事件
    this.socket.emit(event, callback)
  }

  connect() {  // 连接
    return this.state.connect(this)
  }

  disconnect() {  // 断开连接
    return this.state.disconnect(this)
  }
}
