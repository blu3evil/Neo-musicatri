import { io } from 'socket.io-client'
import { ElNotification } from 'element-plus'
import { store } from '@/storage'
import { Events } from '@/sockets/events.js'
import { Result } from '@/common.js'

const config = store.getters.config
const i18n = store.getters.i18n

// 初始化用户socket
export const initUserSocket = async () => {
  let userSocket = store.getters.userSocket
  if (userSocket !== null) {
    // 优先中断先前的连接
    userSocket.disconnect()
    userSocket.isConnected = false
  }

  // 连接不存在初始化连接
  const url = `${config['SOCKET_ENDPOINT']}/user`
  const lang = store.getters.activeLanguage
  const socket = new SocketClient(url, lang)

  const result = await socket.connect()

  if (result.isSuccess()) {  // 连接建立成功
    await store.dispatch('setUserSocket', socket) // 设置连接进入vuex
  }
  return result  // 返回结果
}

// socket客户端，基于路径创建不同的socket连接，例如客户socket，管理员socket
export class SocketClient {
  constructor(url, lang='en-US') {
    this.socket = io(url, {
      autoConnect: false, // 取消自动连接
      reconnection: false,  // 禁用重连，手动操作重连逻辑
      transports: ['websocket', 'polling'],  // 使用websocket而不是轮询
      extraHeaders: {
        // 自定义请求头，指定携带语言实现前后端联调下的本地化
        'Accept-Language': 'en-US',
      },
    })
    this.isConnected = false
  }

  // 手动连接
  connect() {
    return new Promise(async resolve => {
      if (this.isConnected) {  // 已经连接
        resolve(new Result(200))
        return
      }

      this.socket.connect()  // 执行连接
      let timeoutId = 0  // 自动检测超时

      // 连接失败
      this.socket.once(Events.CONNECT_ERROR, response => {
        clearTimeout(timeoutId)  // 清理超时
        console.log(response)
        this.isConnected = false
        resolve(Result.fromJSON(response))
        ElNotification({  // 弹出提示
          title: i18n.global.t('sockets.socket-client.socket_error_title'),
          message: i18n.global.t('sockets.socket-client.socket_connect_error_message'),
          position: 'bottom-right',
        })
      })

      // 连接建立成功
      this.socket.once(Events.CONNECT_SUCCESS, response => {
        clearTimeout(timeoutId)  // 清理超时
        console.log(response)
        this.isConnected = true

        // 绑定断开连接事件
        this.socket.once('disconnect', () => {
          this.isConnected = false  // 设置连接状态量为false
          ElNotification({
            title: i18n.global.t('sockets.socket-client.socket_error_title'),
            message: i18n.global.t('sockets.socket-client.socket_disconnect_message'),
            position: 'bottom-right',
          })
          this.socket.disconnect()
        })

        resolve(Result.fromJSON(response))
        ElNotification({  // 弹出提示
          title: i18n.global.t('sockets.socket-client.socket_success_title'),
          message: i18n.global.t('sockets.socket-client.socket_connect_message'),
          position: 'bottom-right',
        })
      })

      this.socket.once('connect', () => {})  // 空实现
      this.socket.once('connect_error', () => {})  // 连接错误

      // 超时处理
      timeoutId = setTimeout(() => {
        this.isConnected = false
        this.socket.off(Events.CONNECT_ERROR)  // 移除事件监听
        this.socket.off(Events.CONNECT_SUCCESS)
        resolve(new Result(
          601, i18n.global.t('sockets.socket-client.socket_connect_timeout'),))
      }, config['SOCKET_CONNECT_TIMEOUT'])
    })
  }

  // 手动断开连接
  disconnect() {
    if (this.isConnected) {
      this.socket.disconnect()
    }
  }
}