const userPrototype = {
  'id': '000175',
  'avatar': null,
  'username': 'pineclone',
  'global_name': 'pineclone',
  'roles': [],
}

const userAvatarPrototype = {
  url: null,
  status: 'unset'
}

export default {
  namespace: true,
  state: () => ({
    currentUser: userPrototype,  // 当前用户(此处作占位)
    userAvatar: userAvatarPrototype,  // 当前用户头像
    userSocketStatus: 'unconnected',  // userSocket当前状态
    adminSocketStatus: 'unconnected',  // adminSocket当前状态
  }),
  mutations: {
    // 设置当前用户
    setUserSocketStatus(state, status) {
      state.userSocketStatus = status
    },
    setAdminSocketStatus(state, status) {
      state.adminSocketStatus = status
    },
    setCurrentUser(state, user) {
      state.currentUser = user
    },
    setUserAvatar(state, obj) {
      state.userAvatar = obj
    },
    setUserAvatarURL(state, url) {
      state.userAvatar.url = url
    },
    setUserAvatarStatus(state, status) {
      state.userAvatar.status = status
    }
  },
  actions: {
    setUserSocketStatus({ commit }, status) {
      commit('setUserSocketStatus', status)
    },
    setAdminSocketStatus({ commit }, status) {
      commit('setAdminSocketStatus', status)
    },
    setUserAvatarStatus({ commit }, status) {
      commit('setUserAvatarStatus', status)
    },
    setUserAvatarURL({ commit }, status) {
      commit('setUserAvatarURL', status)
    },
    setCurrentUser({ commit }, user) {
      commit('setCurrentUser', user)
    },
    // 清除当前用户数据，在用户登出的时候使用
    clearCurrentUser({ commit }) {
      commit('setCurrentUser', userPrototype)  // 重置用户数据
      commit('setUserAvatar', userAvatarPrototype)  // 重置用户头像
    }
  },
  getters: {
    adminSocketStatus: state => state.adminSocketStatus,  // 管理员连接状态
    userSocketStatus: state => state.userSocketStatus,  // 用户连接当前状态
    userAvatarStatus: state => state.userAvatar.status,
    userAvatarURL: state => state.userAvatar.url,
    currentUser: state => state.currentUser,
  },
}













