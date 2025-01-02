// 系统服务
// noinspection JSUnresolvedReference
import { musicatriClient } from '@/services/axios-client.js'
import { config } from '@/config.js'

const urlPrefix = '/system'

class SystemService {
  // 获取服务器当前健康状态
  getSystemHealth() {
    return musicatriClient.get(`${urlPrefix}/health`)
  }

  // 获取服务信息
  getSystemInfo() {
    return musicatriClient.get(`${urlPrefix}/info`)
  }
}

export const systemService = new SystemService()
