// 系统服务
// noinspection JSUnresolvedReference

import { useClient } from '@/services/axios-client.js'
import store from '@/storage/index.js'

const client = useClient()  // 客户端

const urlPrefix = '/system'

// 获取服务器当前健康状态
export const getSystemHealth = () => client.get(`${urlPrefix}/health`)

const config = store.getters.config
const HEALTH_CHECK_INTERVAL = config['HEALTH_CHECK_INTERVAL']

class HealthCheck {
  constructor() {
    this.healthcheckIntervalId = 0
  }

  begin(onConnectionError) {
    clearInterval(this.healthcheckIntervalId) // 避免重复创建
    this.healthcheckIntervalId = setInterval(async () => {
      // 执行健康检查
      const result = await getSystemHealth()
      if (result.isConnectionError()) {
        onConnectionError(result)
      }
    }, HEALTH_CHECK_INTERVAL * 1000)
  }

  stop() {
    clearInterval(this.healthcheckIntervalId)
  }
}

const createHealthCheck = () => {
  return new HealthCheck()
}

export {
  createHealthCheck
}
