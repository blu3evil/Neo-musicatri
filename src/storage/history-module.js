const historyPrototype = {
  settingsHistory: 'appearance',
  workspaceHistory: 'portal',
  appManagementHistory: 'overview',
  userManagementHistory: 'overview',
  musiclibManagementHistory: 'overview',
}
export default {
  namespace: true,
  state: () => ({
    history: historyPrototype,
  }),
  mutations: {
    setHistory(state, { name, history }) {
      state.history[name] = history
    },
    clearHistory(state) {
      state.history = historyPrototype
    },
  },
  actions: {
    setHistory({ commit }, payload) {
      commit('setHistory', payload)
    },
    clearHistory({ commit }) {  // 清除历史
      commit('clearHistory')
    },
  },
  getters: {
    history: state => state.history,
  },
}
