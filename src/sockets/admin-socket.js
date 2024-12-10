// noinspection JSUnresolvedReference

import { config } from '@/config.js'
import { i18n } from '@/locale/index.js'
import { Events } from '@/sockets/events.js'
import { store } from '@/storage/index.js'
import { io } from 'socket.io-client'
import { Result } from '@/common.js'
import { AbstractState, StateContext } from '@/pattern.js'
import { ToastMessage } from '@/utils/ui-helper.js'

class SocketState extends AbstractState {
  async connect(context) {
    return new Result(400, 'unsupported operation')
  }
  async disconnect(context) {
    return new Result(400, 'unsupported operation')
  }
}

// 已连接
class ConnectedState extends SocketState {
  async enter(context) {
    await store.dispatch('setAdminSocketStatus', 'connected')
  }

  async connect(context) {
    return new Result(200, 'already connected')
  }

  async disconnect(context) {
    context.socket.off('disconnect') // 清除原始断开连接事件
    return await new Promise(resolve => {
      let timeoutId = 0 // 检测超时
      timeoutId = setTimeout(() => {
        resolve(new Result(601)) // 超时处理
      }, context.timeout)

      context.socket.once('disconnect', () => {
        clearTimeout(timeoutId) // 清除超时事件
        context.setState(new UnconnectedState())
        resolve(new Result(200, 'disconnect success'))
      })
      context.socket.disconnect()
    })
  }
}

// 未连接状态
class UnconnectedState extends SocketState {
  async enter(context) {
    context.socket.disconnect()
    context.socket = null // 清除socket
    await store.dispatch('setAdminSocketStatus', 'unconnected')
  }

  fadeout(context) {
    context.socket.off(Events.SERVER.CONNECT.ACCEPT) // 移除事件监听
    context.socket.off(Events.SERVER.CONNECT.REJECT)
  }

  async disconnect(context) {
    return new Result(200, 'already disconnected')
  }

  async connect(context) {
    await store.dispatch('setAdminSocketStatus', 'connecting')
    return new Promise(resolve => {
      // 建立连接
      let timeoutId = 0
      timeoutId = setTimeout(() => {
        context.setState(new UnconnectedState()) // 未连接状态
        resolve(
          new Result(
            601,
            i18n.global.t('sockets.admin-socket.connect_timeout'),
          ),
        ) // 超时处理
      }, context.timeout)

      context.socket = io(context.url, {
        // 将socket对象挂载到上下文
        reconnection: false, // 禁用重连，手动操作重连逻辑
        transports: ['websocket', 'polling'], // 使用websocket而不是轮询
      })

      // 连接失败
      context.socket.once(Events.SERVER.CONNECT.REJECT, response => {
        clearTimeout(timeoutId) // 清理超时
        context.setState(new UnconnectedState()) // 未连接状态
        resolve(Result.fromJSON(response))
      })

      // 连接建立成功
      context.socket.once(Events.SERVER.CONNECT.ACCEPT, async response => {
        clearTimeout(timeoutId) // 清理超时
        context.socket.once('disconnect', () => {
          context.setState(new UnconnectedState()) // 未连接状态
          ToastMessage.error(i18n.global.t('sockets.admin-socket.connect_shutdown'))
        })
        context.setState(new ConnectedState()) // 已连接状态
        resolve(Result.fromJSON(response))
      })
    })
  }
}

class UserSocketContext extends StateContext {
  constructor() {
    super(new UnconnectedState())
    this.url = `${config['SOCKET_ENDPOINT']}/admin`
    this.timeout = config['SOCKET_CONNECT_TIMEOUT']
  }

  connect() {
    return this.state.connect(this)
  }

  disconnect() {
    return this.state.disconnect(this)
  }
}

const adminSocketContext = new UserSocketContext()
export { adminSocketContext }
