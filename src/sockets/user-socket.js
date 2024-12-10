// noinspection JSUnresolvedReference

import { config } from '@/config.js'
import { Events } from '@/sockets/events.js'
import { store } from '@/storage/index.js'
import { AbstractState, StateContext } from '@/pattern.js'
import { io } from 'socket.io-client'
import { Result } from '@/common.js'
import { userService } from '@/services/user-service.js'
import { ToastMessage } from '@/utils/ui-helper.js'
import { i18n } from '@/locale/index.js'

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
    await store.dispatch('setUserSocketStatus', 'connected')
  }

  async connect(context) {
    return new Result(200, 'already connected')
  }

  async disconnect(context) {
    context.socket.off('disconnect') // 清除原始断开连接事件
    return await new Promise(resolve => {
      let timeoutId = 0 // 自动检测超时
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
    await store.dispatch('setUserSocketStatus', 'unconnected')
  }

  fadeout(context) {
    context.socket.off(Events.SERVER.CONNECT.ACCEPT) // 移除事件监听
    context.socket.off(Events.SERVER.CONNECT.REJECT)
  }

  async disconnect(context) {
    return new Result(200, 'already disconnected')
  }

  async connect(context) {
    await store.dispatch('setUserSocketStatus', 'connecting')
    return new Promise(resolve => {
      // 建立连接

      let timeoutId = 0
      timeoutId = setTimeout(() => {
        context.setState(new UnconnectedState()) // 未连接状态
        resolve(new Result(601)) // 超时处理
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
        // 初始化用户信息
        const result = await userService.loadUserDetails()
        if (result.isSuccess()) {
          // 挂载断开连接事件
          context.socket.once('disconnect', () => {
            context.setState(new UnconnectedState()) // 未连接状态
            ToastMessage.error(i18n.global.t('sockets.user-socket.connect_shutdown'))
          })
          // 初始化用户头像
          userService.loadUserAvatar().then()
          context.setState(new ConnectedState()) // 已连接状态
          resolve(Result.fromJSON(response))

        } else {
          // 拉取用户信息失败
          context.setState(new UnconnectedState())
          resolve(result)
        }
      })
    })
  }
}

class UserSocketContext extends StateContext {
  constructor() {
    super(new UnconnectedState())
    this.url = `${config['SOCKET_ENDPOINT']}/user`
    this.timeout = config['SOCKET_CONNECT_TIMEOUT']
  }

  connect() {
    return this.state.connect(this)
  }

  disconnect() {
    return this.state.disconnect(this)
  }
}

const userSocketContext = new UserSocketContext()
export { userSocketContext }
