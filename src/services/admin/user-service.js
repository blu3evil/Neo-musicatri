// 用户服务模块
import { musicatriClient } from '@/services/axios-client.js'

const urlPrefix = '/admin/users'
class AdminUserService {
  // 获取用户数据概览
  getUsersPreview(condition={}) {
    return musicatriClient.post(`${urlPrefix}/preview`, condition)
  }
  // 获取指定用户账户详情
  getUserDetails(userId) {
    return musicatriClient.get(`${urlPrefix}/${userId}/details`)
  }
  // 获取所有权限级别
  getAllRoles() {
    return musicatriClient.get(`${urlPrefix}/roles`)
  }
  // 修改用户信息
  patchUser(userId, data) {
    return musicatriClient.patch(`${urlPrefix}/${userId}`, data)
  }
  // 删除用户
  deleteUser(userId) {
    return musicatriClient.delete(`${urlPrefix}/${userId}`)
  }
}

export const adminUserService = new AdminUserService();
