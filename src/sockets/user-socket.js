// 用户socketio连接类
import { i18n } from '@/locale/index.js'
import { config } from '@/config.js'
import { Events } from '@/sockets/events.js'
import { store } from '@/storage/index.js'
import { SocketClient } from '@/sockets/socket-client.js'
import { ToastMessage } from '@/utils/ui-helper.js'

class UserSocket extends SocketClient {
  constructor() {
    super()
    this.url=`${config['SOCKET_ENDPOINT']}/user`
    this.timeout=config['SOCKET_CONNECT_TIMEOUT']
  }

  // 连接到user socket通道
  // noinspection JSCheckFunctionSignatures
  async connect() {
    const result = await super.connect()
    if (result.isSuccess()) {
      // 连接成功，挂载断开连接事件，在断开连接时清除登录状态
      this.socket.once('disconnect', () => {
        store.dispatch('clearCurrentUser')  // 清除当前用户信息
        store.dispatch('setUserSocketConnectStatus', false)  // 设置登入状态(阻塞)
      })

      // 阻塞后向后端请求用户信息，避免userSocketConnected状态量更新不及时
      const flag = await new Promise(resolve => {
        // 给定超时，防止后端无响应
        let timeoutId = setTimeout(() => {
          ToastMessage.error(i18n.global.t('sockets.user-socket-client.fetch_user_timeout'))
          resolve()
        }, config['REQUEST_TIMEOUT'])

        this.socket.emit(Events.CLIENT.USER.FETCH, (result) => {
          if (result.code === 200) {
            // 成功拉取用户数据，将用户数据设置到vuex
            clearTimeout(timeoutId)
            store.dispatch('setCurrentUser', result.data)
            store.dispatch('setUserSocketConnectStatus', true)
            resolve(true)  // 连接建立成功(阻塞)
          } else {
            // 拉取用户数据失败
            clearTimeout(timeoutId)
            ToastMessage.error(i18n.global.t('sockets.user-socket-client.fetch_user_error'))
            resolve(false)  // 拉取用户数据失败，连接建立失败
          }
        })
      })
    }
    return result  // 断开连接
  }
}

const userSocketClient = new UserSocket()
export { userSocketClient }
