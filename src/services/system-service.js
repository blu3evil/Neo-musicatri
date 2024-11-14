// 系统服务
// noinspection JSUnresolvedReference

import { useClient } from '@/services/axios-client.js'
import store from '@/storage/index.js'

const client = useClient()  // 客户端

// 获取服务器当前健康状态
const getSystemHealth = async () => {
  return await client.get('/system/health')
}

export { getSystemHealth }
const config = store.getters.config
const HEALTH_CHECK_INTERVAL = config['HEALTH_CHECK_INTERVAL']

class HealthCheck {
  constructor() {
    this.healthcheckIntervalId = 0
  }

  begin(onConnectError) {
    clearInterval(this.healthcheckIntervalId) // 避免重复创建
    this.healthcheckIntervalId = setInterval(async () => {
      // 执行健康检查
      try {
        await getSystemHealth()
      } catch (error) {
        if (error.code === 'ERR_NETWORK' || error.code === 'ECONNABORTED') {
          clearInterval(this.healthcheckIntervalId)
          onConnectError()
        }
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
export { createHealthCheck }
