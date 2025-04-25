// 用户服务模块
import { musicatriClient } from '@/services/axios-client.js'

class UserServiceV1 {
  constructor (urlPrefix) {
    self.urlPrefix = urlPrefix
  }
  // 获取当前用户详情信息
  getCurrentUserDetails() {
    return musicatriClient.get(`${urlPrefix}/me/details`)
  }
}

export const userServiceV1 = new UserServiceV1('/v1/users');
