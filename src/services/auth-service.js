// 认证服务
// noinspection JSUnresolvedReference
import { store } from '@/storage/index.js'
import { musicatriClient } from '@/services/axios-client.js'
import { Result } from '@/common.js'

class AuthServiceV1 {
  constructor (urlPrefix) {
    this.urlPrefix = urlPrefix
  }

  // 获取认证路径
  getAuthorizeUrl() {
    return musicatriClient.get(`${this.urlPrefix}/authorize-url`)
  }

  // 授权
  authorize(code) {
    return musicatriClient.post(`${this.urlPrefix}/authorize`, { code })
  }

  // 登入
  login() {
    return musicatriClient.get(`${this.urlPrefix}/login`)
  }

  logout() {
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
  login() {
    return musicatriClient.get(`${this.urlPrefix}/login`)
  }

  // 认证，通过discord oauth2认证回调取得code码进行oauth2登录校验
  async authorize(code) {  // 授权
    const result = await musicatriClient.post(`${this.urlPrefix}/authorize`, { code: code })
    if (result.isSuccess()) {
      // 认证成功，存储AccessToken相关信息
      const data = result.data
      await store.dispatch('storeAuthToken', {
        tokenType: data['token_type'],
        expiresAt: data['expires_at'],
        accessToken: data['access_token']
      })
    }
    return result
  }

  // 登出，调用登出接口吊销用户的jwt凭证
  logout() {
    return musicatriClient.delete(`${this.urlPrefix}/logout`)
  }

  // 更高效的用户身份校验
  async validate(roles=null, strict=false) {
    if (roles === null || roles === undefined) roles = ['user']

    if (strict) {
      // 严格检查
      return await musicatriClient.post(`${this.urlPrefix}/validate`, { roles })
    } else {
      // 非严格检查
      if (!store.getters.currentUser.id === null) {  // 登录校验
        return new Result(403)
      }

      const current_user_id = store.getters.currentUser.id
      const current_user_roles = store.getters.currentUser.roles

      if (current_user_roles === null || current_user_roles === undefined) {
        return new Result(403)
      }

      if (!roles.every(role => current_user_roles.includes(role))) {
        return new Result(403)
      }

      return new Result(200, null, {
        user_id: current_user_id,
        roles: current_user_roles
      })
    }
  }
}

export const authServiceV1 = new AuthServiceV1('/v1/auth')
export const authServiceV2 = new AuthServiceV2('/v2/auth')
