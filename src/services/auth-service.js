// 认证服务
// noinspection JSUnresolvedReference
import { store } from '@/storage/index.js'
import { musicatriClient } from '@/services/axios-client.js'

const urlPrefix = '/auth'
class AuthService {
  // 获取认证路径
  getAuthorizeUrl() {
    return musicatriClient.get(`${urlPrefix}/authorize-url`)
  }

  // 授权
  userAuthorize(code) {
    return musicatriClient.post(`${urlPrefix}/authorize`, { code: code })
  }

  // 登入
  userLogin() {
    return musicatriClient.get(`${urlPrefix}/login`)
  }

  userLogout() {
    return musicatriClient.delete(`${urlPrefix}/logout`)
  }

  // 严格权限校验
  async verifyRole(role) {
    return musicatriClient.get(`${urlPrefix}/role/${role}`)
  }

  // 严格登录校验
  async verifyLogin() {
    return musicatriClient.get(`${urlPrefix}/status`)
  }

  // 非严格权限校验
  checkRole(role) {
    return store.getters.currentUser.roles.includes(role)
  }

  // 非严格登录校验
  checkLogin() {
    return store.getters.currentUser.roles.includes('user')
  }
}

export const authService = new AuthService()
