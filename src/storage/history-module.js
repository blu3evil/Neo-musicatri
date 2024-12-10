export default {
  namespace: true,
  state: () => ({
    activeSettingMenuItem: 'appearance',  // 当前激活的设置页面
    activeWorkspaceMenuItem: 'portal',  // 当前激活的工作台页面
    activeDashboardMenuItem: 'overview',  // dashboard当前页面
  }),
  mutations: {
    setActiveSettingMenuItem(state, page) {
      state.activeSettingMenuItem = page
    },
    setActiveWorkspaceMenuItem(state, page) {
      state.activeWorkspaceMenuItem = page
    },
    setActiveDashboardMenuItem(state, page) {
      state.activeDashboardMenuItem = page
    }
  },
  actions: {
    setActiveSettingMenuItem({ commit }, page) {
      commit('setActiveSettingMenuItem', page)
    },
    setActiveWorkspaceMenuItem({ commit }, page) {
      commit('setActiveWorkspaceMenuItem', page)
    },
    setActiveDashboardMenuItem({ commit }, page) {
      commit('setActiveDashboardMenuItem', page)
    }
  },
  getters: {
    // activeSettingPage GETTER
    activeSettingMenuItem: state => state.activeSettingMenuItem,
    activeWorkspaceMenuItem: state => state.activeWorkspaceMenuItem,
    activeDashboardMenuItem: state => state.activeDashboardMenuItem,
  },
}
