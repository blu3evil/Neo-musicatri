// 服务器信息模块
import { systemServiceV1 } from '@/services/system-service.js'
import { globalEventbus } from '@/mitt/global-eventbus.js'
import { Events } from '@/events.js'
const systemInfoPrototype = {
  'name': 'undefined',
  'version': 'undefined',
  'description': 'undefined',
}
export default {
  namespace: true,
  state: () => ({
    systemInfo: null,  // 后端信息，来源为后端配置文件
  }),
  mutations: {
    setSystemInfo(state, info) {
      state.systemInfo = info
    },
  },
  actions: {
    setSystemInfo({ commit }, info) {
      commit('setSystemInfo', info)
    },
    // 初始化服务器信息
    async loadSystemInfo({ commit }) {
      const result = await systemServiceV1.getSystemInfo()
      if (result.isSuccess()) {
        globalEventbus.emit(Events.MITT.SYSTEM_INFO.LOAD_SUCCESS)
        commit('setSystemInfo', result.data)  // 成功获取服务信息
      } else {
        globalEventbus.emit(Events.MITT.SYSTEM_INFO.LOAD_FAILED)
        commit('setSystemInfo', systemInfoPrototype)  // 获取信息失败
      }
      return result
    }
  },
  getters: {
    systemInfo: state => state.systemInfo,
  },
}

