// socket-io模块
export default {
  namespace: true,
  state: () => ({
    socket: null,  // socketio对象
    isConnected: false,  // 连接状态
    user: null,  // 当前用户
  }),
  mutations: {
    // 设置socket
    setSocket: (state, socket) => {
      state.socket = socket
    },
    // 设置当前连接状态
    setConnectionStatus(state, status) {
      state.isConnected = status
    },
    // 设置当前用户
    setUser: (state, user) => {
      state.user = user
    }
  },
  actions: {
  },
  getters: {
    isConnected: state => state.isConnected,
    user: state => state.user,
    socket: state => state.socket,
  },
}
