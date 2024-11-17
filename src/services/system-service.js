// 系统服务
// noinspection JSUnresolvedReference

import { useClient } from '@/services/axios-client.js'
import store from '@/storage/index.js'

const client = useClient()  // 客户端

const urlPrefix = '/system'



class SystemService {
  // 获取服务器当前健康状态
  getSystemHealth() {
    return client.get(`${urlPrefix}/health`)
  }

  // 获取服务信息
  getSystemInfo() {
    return client.get(`${urlPrefix}/info`)
  }
}

const systemService = new SystemService()
export const useSystemService = () => systemService

const config = store.getters.config
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

const useSystemHealthCheck = () => {
  return new SystemHealthCheck()
}

export {
  useSystemHealthCheck
}
