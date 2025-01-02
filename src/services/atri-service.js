import { musicatriClient } from '@/services/axios-client.js'
import { globalEventbus } from '@/mitt/global-eventbus.js'
import { Events } from '@/events.js'

const urlPrefix = '/atri'
class AuthService {
  getStatus() {  // 获取状态
    return musicatriClient.get(`${urlPrefix}/status`)
  }

  startAtri() {  // 开始
    return musicatriClient.post(`${urlPrefix}/start`)
  }

  stopAtri() {  // 停止
    return musicatriClient.get(`${urlPrefix}/stop`)
  }

  emitMessage(message) {
    return musicatriClient.get(`${urlPrefix}/test/${message}`)
  }
}

export const atriService = new AuthService()
