// 服务器信息模块
import { globalEventbus } from '@/mitt/global-eventbus.js'
import { atriService } from '@/services/atri-service.js'
// import { adminSocketContext } from '@/sockets/admin-socket.js'
import { Events } from '@/events.js'
import { Result } from '@/common.js'

export default {
  namespace: true,
  state: () => ({
    atriInfo: {
      status: 'stopped'  // 亚托莉状态
    }
  }),
  mutations: {
    setAtriInfo(state, info) {
      state.atriInfo = info
    },
    setAtriStatus(state, status) {
      state.atriInfo.status = status
    }
  },
  actions: {
    setAtriStatus({ commit }, status) {
      commit('setAtriStatus', status)
    },
    // 加载亚托莉状态
    async loadAtriStatus({ commit }) {
      const result = await atriService.getStatus()
      if (result.isSuccess()) {
        globalEventbus.emit(Events.MITT.ATRI.STATE.LOAD_SUCCESS)
        commit('setAtriStatus', result.data.status)  // 成功获取亚托莉状态
      } else {
        globalEventbus.emit(Events.MITT.ATRI.STATE.LOAD_FAILED)
        commit('setAtriStatus', 'failed')  // 加载状态失败
      }
    },

    // 启动亚托莉
    async startAtri({ commit, getters }) {
      // if (getters.atriInfo.status !== 'started')
      //   return new Result(400, 'unsupported operation')
      const result = atriService.startAtri()
      return result
    },

    async stopAtri({ commit, getters }) {
      if (getters.atriInfo.status !== 'started')
        return new Result(400, 'unsupported operation')

      commit('setAtriStatus', 'stopping')  // 防抖
      const result = atriService.stopAtri()  // 执行停止亚托莉
      if (result.isSuccess()) {  // 成功执行停止工作流
        globalEventbus.emit(Events.MITT.ATRI.STOP_ACTION.SUCCESS, result.message)

        // 监听socketio事件处理后续



      } else {  // 执行停止工作流失败
        globalEventbus.emit(Events.MITT.ATRI.STOP_ACTION.FAILED, result.message)
        commit('setAtriStatus', 'started')  // 恢复原始状态
      }
    }
  },
  getters: {
    atriInfo: state => state.atriInfo
  },
}

