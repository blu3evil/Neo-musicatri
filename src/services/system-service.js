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
const SYSTEM_HEALTH_CHECK_INTERVAL = config['SYSTEM_HEALTH_CHECK_INTERVAL']

class SystemHealthCheck {
  constructor() {
    this.healthcheckIntervalId = 0
  }

  begin(onConnectionError) {
    clearInterval(this.healthcheckIntervalId) // 避免重复创建
    this.healthcheckIntervalId = setInterval(async () => {
      // 执行健康检查
      const result = await systemService.getSystemHealth()
      if (result.isConnectionError()) {
        onConnectionError(result)
      }
    }, SYSTEM_HEALTH_CHECK_INTERVAL)
  }

  stop() {
    clearInterval(this.healthcheckIntervalId)
  }
}
