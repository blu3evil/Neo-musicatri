// 用户服务模块
import { musicatriClient } from '@/services/axios-client.js'

const urlPrefix = '/users'
class UserService {
  // 获取当前用户详情信息
  getUserDetails(user_id=null) {
    if (user_id == null) {
      return musicatriClient.get(`${urlPrefix}/me/details`)
    }
  }
}

export const userService = new UserService();
