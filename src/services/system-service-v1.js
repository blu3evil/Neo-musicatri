// 系统服务
// noinspection JSUnresolvedReference
import { musicatriClient } from '@/services/axios-client.js'

class SystemServiceV1 {
  constructor(urlPrefix) {
    this.urlPrefix = urlPrefix
  }
  // 获取服务器当前健康状态
  getSystemHealth() {
    return musicatriClient.get(`${this.urlPrefix}/health`)
  }

  // 获取服务信息
  getSystemInfo() {
    return musicatriClient.get(`${this.urlPrefix}/info`)
  }
}

export const systemServiceV1 =
  new SystemServiceV1('/v1/system')
