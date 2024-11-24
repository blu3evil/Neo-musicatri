// 认证服务
// noinspection JSUnresolvedReference
import { useClient } from '@/services/axios-client.js'
const client = useClient()  // 客户端

import { store } from '@/storage/index.js'
await store.dispatch('loadConfig')  // 等待加载完成

const urlPrefix = '/auth'
class AuthService {
  // 获取认证路径
  getAuthorizeUrl() {
    return client.get(`${urlPrefix}/authorize-url`)
  }

  // 授权
  userAuthorize(code) {
    return client.post(`${urlPrefix}/authorize`, { code: code })
  }

  // 登入
  userLogin() {
    return client.get(`${urlPrefix}/login`)
  }

  // 获取当前登录状态
  getUserLoginStatus() {
    return client.get(`${urlPrefix}/status`)
  }

  verifyUserLoginStatus() {
    return store.getters.userSocket !== null && store.getters.userSocket.isConnected !== null
  }
}

export const authService = new AuthService()
