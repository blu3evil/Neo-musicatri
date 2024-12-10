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

  // 校验用户登入状态接口
  verifyLogin() {
    // 通过socket连接状态判断登录
    return store.getters.userSocketStatus === 'connected'
  }

  verifyAdmin() {
    return store.getters.adminSocketStatus === 'connected'
  }

  // 校验用户是否包含目标权限
  verifyRole(role) {
    const userRoles = store.getters.currentUser.roles
    return userRoles.length > 0 && userRoles.includes(role);
  }
}

export const authService = new AuthService()
