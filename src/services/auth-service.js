// 认证服务
// noinspection JSUnresolvedReference
import { store } from '@/storage/index.js'
import { musicatriClient } from '@/services/axios-client.js'

class AuthServiceV1 {
  constructor (urlPrefix) {
    this.urlPrefix = urlPrefix
  }

  // 获取认证路径
  getAuthorizeUrl() {
    return musicatriClient.get(`${this.urlPrefix}/authorize-url`)
  }

  // 授权
  userAuthorize(code) {
    return musicatriClient.post(`${this.urlPrefix}/authorize`, { code: code })
  }

  // 登入
  userLogin() {
    return musicatriClient.get(`${this.urlPrefix}/login`)
  }

  userLogout() {
    return musicatriClient.delete(`${this.urlPrefix}/logout`)
  }

  // 严格权限校验
  async verifyRole(role) {
    return musicatriClient.get(`${this.urlPrefix}/role/${role}`)
  }

  // 严格登录校验
  async verifyLogin() {
    return musicatriClient.get(`${this.urlPrefix}/status`)
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

class AuthServiceV2 {
  constructor (urlPrefix) {
    this.urlPrefix = urlPrefix
  }

  // 登入
  userLogin() {
    return musicatriClient.get(`${this.urlPrefix}/login`)
  }

  // 授权
  userAuthorize(code) {
    return musicatriClient.post(`${this.urlPrefix}/authorize`, { code: code })
  }

}

export const authServiceV1 = new AuthServiceV1('/v1/auth')
export const authServiceV2 = new AuthServiceV2('/v2/auth')
