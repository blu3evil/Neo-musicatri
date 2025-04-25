// 用户服务模块
import { musicatriClient } from '@/services/axios-client.js'

class AdminUserServiceV1 {
  constructor(urlPrefix) {
    this.urlPrefix = urlPrefix
  }
  // 获取全部用户数据概览，此方法仅适用与小批量数据
  getAllUsersPreview(condition={}) {
    const params = { ...condition }
    return musicatriClient.get(`${this.urlPrefix}/preview/all`, { params })
  }
  // 获取用户数据概览，此方法支持分页查询
  getUserPreview(condition={}) {
    const params = { ...condition }
    return musicatriClient.get(`${this.urlPrefix}/preview`, { params })
  }
  // 获取指定用户账户详情
  getUserDetails(userId) {
    return musicatriClient.get(`${this.urlPrefix}/${userId}/details`)
  }
  // 获取所有权限级别
  getAllRoles() {
    return musicatriClient.get(`${this.urlPrefix}/roles`)
  }
  // 修改用户信息
  patchUser(userId, data) {
    return musicatriClient.patch(`${this.urlPrefix}/${userId}`, data)
  }
  // 删除用户
  deleteUser(userId) {
    return musicatriClient.delete(`${this.urlPrefix}/${userId}`)
  }
}

export const adminUserServiceV1 =
  new AdminUserServiceV1('/v1/admin/users');
