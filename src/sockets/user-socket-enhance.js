// noinspection JSUnresolvedReference

import { i18n } from '@/locale/index.js'
import { config } from '@/config.js'
import { Events } from '@/sockets/events.js'
import { store } from '@/storage/index.js'
import { ToastMessage } from '@/utils/ui-helper.js'
import { AbstractState, StateContext } from '@/pattern.js'
import { io } from 'socket.io-client'
import { Result } from '@/common.js'


class SocketState extends AbstractState {
  connect(context) {}
  disconnect(context) {}
}

class VanillaSocketState extends SocketState {
  async enter(context) {
    await store.dispatch('setUserSocketStatus', 'vanilla')
  }

  async connect(context) {
    const result = await this.doConnect(context)
    if (result.isSuccess()) {
      // 连接成功，挂载断开连接事件，在断开连接时清除登录状态
      this.socket.once('disconnect', () => {
        store.dispatch('clearCurrentUser') // 清除当前用户信息
        store.dispatch('setUserSocketConnectStatus', false) // 设置登入状态(阻塞)
      })

      // 阻塞后向后端请求用户信息，避免userSocketConnected状态量更新不及时

    }

    return result
  }

  doFetchUser(context) {
    return new Promise(resolve => {
      // 给定超时，防止后端无响应
      let timeoutId = setTimeout(() => {
        ToastMessage.error(
          i18n.global.t('sockets.user-socket-client.fetch_user_timeout'),
        )
        resolve()
      }, config['REQUEST_TIMEOUT'])

      this.socket.emit(Events.CLIENT.USER.FETCH, async result => {
        if (result.code === 200) {
          // 成功拉取用户数据，将用户数据设置到vuex
          clearTimeout(timeoutId)
          await store.dispatch('setCurrentUser', result.data)
          await store.dispatch('setUserSocketConnectStatus', true)
          resolve(true) // 连接建立成功(阻塞)
        } else {
          // 拉取用户数据失败
          clearTimeout(timeoutId)
          ToastMessage.error(
            i18n.global.t('sockets.user-socket-client.fetch_user_error'),
          )
          resolve(false) // 拉取用户数据失败，连接建立失败
        }
      })
    })
  }

  doConnect(context) {
    return new Promise(resolve => {
      // 构建连接对象
      this.socket = io(context.url, {
        autoConnect: false, // 取消自动连接
        reconnection: false, // 禁用重连，手动操作重连逻辑
        transports: ['websocket', 'polling'], // 使用websocket而不是轮询
      })

      this.socket.connect() // 执行连接
      let timeoutId = 0 // 自动检测超时

      // 连接失败
      this.socket.once(Events.SERVER.CONNECT.REJECT, response => {
        clearTimeout(timeoutId) // 清理超时
        resolve(Result.fromJSON(response))
      })

      // 连接建立成功
      this.socket.once(Events.SERVER.CONNECT.ACCEPT, response => {
        clearTimeout(timeoutId) // 清理超时
        resolve(Result.fromJSON(response))
      })

      timeoutId = setTimeout(() => {
        // 超时处理
        this.socket.disconnect()
        this.socket.off(Events.SERVER.CONNECT.ACCEPT) // 移除事件监听
        this.socket.off(Events.SERVER.CONNECT.REJECT)
        resolve(new Result(601))
      }, context.timeout)
    })
  }

  disconnect(context) {
    super.disconnect(context)
  }
}

class UserSocket extends StateContext {
  constructor() {
    super(new VanillaSocketState())
    this.context.url = `${config['SOCKET_ENDPOINT']}/user`
    this.context.timeout = config['SOCKET_CONNECT_TIMEOUT']
  }

  // 连接到user socket通道
  // noinspection JSCheckFunctionSignatures
  connect() {
    return this.state.connect()
  }

  disconnect() {
    return this.state.disconnect()
  }
}

const userSocketClient = new UserSocket()
export { userSocketClient }
