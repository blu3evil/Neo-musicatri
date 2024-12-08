import { io } from 'socket.io-client'
import { Events } from '@/sockets/events.js'
import { Result } from '@/common.js'

// socket客户端，基于路径创建不同的socket连接，例如客户socket，管理员socket
export class SocketClient {
  constructor() {
    this.url = 'http://localhost:5000'
    this.timeout = 5000
    this.socket = null  // 维护socketio连接对象
  }

  // 执行连接socketio
  connect() {
    return new Promise(async resolve => {
      // 构建连接对象
      this.socket = io(
        this.url, {
        autoConnect: false, // 取消自动连接
        reconnection: false,  // 禁用重连，手动操作重连逻辑
        transports: ['websocket', 'polling'],  // 使用websocket而不是轮询
      })

      this.socket.connect()  // 执行连接
      let timeoutId = 0  // 自动检测超时

      // 连接失败
      this.socket.once(Events.SERVER.CONNECT.REJECT, response => {
        clearTimeout(timeoutId)  // 清理超时
        resolve(Result.fromJSON(response))
      })

      // 连接建立成功
      this.socket.once(Events.SERVER.CONNECT.ACCEPT, response => {
        clearTimeout(timeoutId)  // 清理超时
        resolve(Result.fromJSON(response))
      })

      timeoutId = setTimeout(() => {  // 超时处理
        this.socket.disconnect()
        this.socket.off(Events.SERVER.CONNECT.ACCEPT)  // 移除事件监听
        this.socket.off(Events.SERVER.CONNECT.REJECT)
        resolve(new Result(601))
      }, this.timeout)
    })
  }

  // 手动断开连接
  disconnect() {
    this.socket.disconnect()
    this.socket = null
  }
}

