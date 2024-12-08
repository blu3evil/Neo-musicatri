// 用户socketio连接类
import { i18n } from '@/locale/index.js'
import { config } from '@/config.js'
import { store } from '@/storage/index.js'
import { SocketClient } from '@/sockets/socket-client.js'
import { ToastMessage } from '@/utils/ui-helper.js'



class AdminSocketClient extends SocketClient {
  constructor() {
    super()  // 设定连接超时时间
    this.url = `${config['SOCKET_ENDPOINT']}/admin`
    this.timeout = config['SOCKET_CONNECT_TIMEOUT']
  }

  // 连接到user socket通道
  // noinspection JSCheckFunctionSignatures
  async connect() {
    // 记录状态
    await store.dispatch('setAdminSocketConnectingStatus', true)
    const result = await super.connect()  // 建立socket连接
    if (result.isSuccess()) {
      // 连接建立成功(阻塞)
      await store.dispatch('setAdminSocketConnectStatus', true)
      this.socket.once('disconnect', () => {  // 绑定断联事件
        // 设置当前管理端连接状态
        store.dispatch('setAdminSocketConnectStatus', false)
      })
    }

    // 恢复状态
    await store.dispatch('setAdminSocketConnectingStatus', false)
    return result  // 不论结果如何返回结果到调用
  }
}

const adminSocketClient = new AdminSocketClient()
export { adminSocketClient }
