// 用户服务模块
import { musicatriClient } from '@/services/axios-client.js'

const urlPrefix = '/users'
class UserService {
  // 获取当前用户详情信息
  getCurrentUserDetails() {
    return musicatriClient.get(`${urlPrefix}/me/details`)
  }
}

export const userService = new UserService();
