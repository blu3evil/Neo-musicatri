// 认证服务
// noinspection JSUnresolvedReference

import { useClient } from '@/services/axios-client.js'
const client = useClient()  // 客户端

import store from '@/storage/index.js'
import { io } from 'socket.io-client'
import { MusicatriResult } from '@/utils.js'
import { ElMessageBox } from 'element-plus'
import { router } from '@/router.js'

await store.dispatch('loadConfig')  // 等待加载完成
const config = store.getters.config
import { i18n } from '@/locale/index.js'

// 登录过期确认标题
const loginStatusExpiredConfirmTitle =
  i18n.global.t('services.auth-service.login_status_expired_message')
const loginStatusExpiredConfirmMessage =
  i18n.global.t('services.auth-service.login_status_expired_title')

const urlPrefix = '/auth'
class AuthService {
  constructor () {
    this.loginStatusHealthCheckInterval = null  // 登录状态健康检查id
  }

  // 获取认证路径
  getAuthorizeUrl() {
    return client.get(`${urlPrefix}/authorize-url`)
  }

  // 授权
  authorize(code) {
    return client.post(`${urlPrefix}/authorize`, { code: code })
  }

  // 登入
  login() {
    return client.get(`${urlPrefix}/login`)
  }

  // 获取当前登录状态
  getLoginStatus() {
    return client.get(`${urlPrefix}/status`)
  }

  // ** 统一登录验证接口 **
  async verifyLoginStatus() {
    return new Promise( async (resolve) => {
      // 检查用户登录状态
      // 判断socketio状态是否已经存在
      if (store.getters.isConnected) {
        // 连接已经建立，直接返回
        console.log('hit existed socket')
        const result = new MusicatriResult(200)
        resolve(result)  // 处于登录状态
        return
      }

      // socketio断开，查询登录状态
      const result = await this.getLoginStatus()
      if (!result.isSuccess()) {
        // 用户未登入，拒绝建立socket链接
        console.log('user have not logged in')
        resolve(new MusicatriResult(401, 'Unauthorized'))
        return
      }

      // 建立连接
      const socket = io(`${config['SOCKET_ENDPOINT']}/user`)

      // 建立连接
      socket.on('connect', () => {
        console.log('connect success')
        store.commit('setConnectionStatus', true)
        store.commit('setSocket', socket)
        this.startLoginStatusHealthCheck()  // 开启登录状态健康检查
        resolve(new MusicatriResult(200))
      })

      // 连接错误
      socket.on('connect_error', error => {
        console.log('connect error')
        store.commit('setConnectionStatus', false)
        resolve(new MusicatriResult(400, 'Socket connection error'))

        // 清理资源
        socket.close()
        socket.removeAllListeners()
      })

      // 断开连接
      socket.on('disconnect', () => {
        console.log('disconnect success')
        store.commit('setConnectionStatus', false)

        // 清理资源
        socket.close()
        socket.removeAllListeners()
        this.stopLoginStatusHealthCheck()  // 停止健康检查
      })
    })
  }

  // 开启登陆状态健康检查
  startLoginStatusHealthCheck() {
    // 已经开启健康检查，直接返回
    if (this.loginStatusHealthCheckInterval) return
    const interval = config['LOGIN_STATUS_HEALTH_CHECK_INTERVAL']
    // 执行登录状态健康检查
    this.loginStatusHealthCheckInterval = setInterval(
      async () => {
        const result = await this.getLoginStatus()  // 查询登陆状态
        if (result.isSuccess()) {
          // 成功登录
        } else {
          // 登陆状态异常，断开socket连接，并且弹出消息框告知用户
          const socket = store.getters.socket;
          if (socket) socket.disconnect()  // 断开socket连接

          ElMessageBox.alert(
            loginStatusExpiredConfirmTitle,
            loginStatusExpiredConfirmMessage,
            {
              confirmButtonText: i18n.global.t(
                'services.auth-service.login_status_expired_confirm',
              ),
              type: 'warning',
              center: true, // 居中显式
              closeOnClickModal: true, // 点击遮罩层自动关闭
              showConfirmButton: false, // 不再显示确认按钮
              showClose: false, // 关闭右上角关闭小叉
            },
          )
            .then(() => router.push('/user/login'))
            .catch(() => router.push('/user/login'))
        }
      }, interval)
  }

  // 停止登陆状态健康检查
  stopLoginStatusHealthCheck() {
    if (this.loginStatusHealthCheckInterval) {
      clearInterval(this.loginStatusHealthCheckInterval);
      this.loginStatusHealthCheckInterval = null;
    }
  }
}

const authService = new AuthService()
export const useAuthService = () => authService
