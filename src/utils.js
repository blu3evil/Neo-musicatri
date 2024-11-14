// 状态模式
class AbstractState {
  // 切入状态时被调用
  enter(context) {
    // 状态执行逻辑
  }

  // 切出状态时被调用
  fadeout(context) {
    // 退出状态逻辑
  }
}

class StateContext {
  constructor () {
    this.state = null
  }

  setState (state) {
    if (this.state !== null) this.state.fadeout(this)  // 状态退出
    this.state = state  // 切换状态
    if (this.state !== null) this.state.enter(this)  // 切入状态
  }
}

// 健康检查
import { useClient } from '@/client.js'
import store from '@/storage/index.js'
const client = useClient()
const config = store.getters.config
const HEALTH_CHECK_INTERVAL = config['HEALTH_CHECK_INTERVAL']

class HealthCheck {
  constructor () {
    this.healthcheckIntervalId = 0
  }

  begin(onConnectError) {
    clearInterval(this.healthcheckIntervalId)  // 避免重复创建
    this.healthcheckIntervalId = setInterval(async () => {
      // 执行健康检查
      try {
        await client.get('/status/health')
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

export {
  AbstractState,
  StateContext,
  createHealthCheck,
}
