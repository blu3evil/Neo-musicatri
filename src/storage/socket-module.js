// socket-io模块
export default {
  namespace: true,
  state: () => ({
    userSocket: null,
    adminSocket: null,  // 管理员socket连接
    user: null,  // 当前用户
  }),
  mutations: {
    // 设置userSocket
    setUserSocket: (state, userSocket) => {
      state.userSocket = userSocket
    },
    // 设置当前用户
    setUser: (state, user) => {
      state.user = user
    },
    setAdminSocket: (state, socket) => {
      state.adminSocket = socket
    }
  },
  actions: {
    setUserSocket({ commit, dispatch }, socket) {
      commit('setUserSocket', socket)
    }
  },
  getters: {
    adminSocket: state => state.adminSocket,
    userSocket: state => state.userSocket,
    user: state => state.user,
  },
}
