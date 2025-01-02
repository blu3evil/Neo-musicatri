import { Result } from '@/common.js'
import { globalEventbus } from '@/mitt/global-eventbus.js'
import { Events } from '@/events.js'
import { discordService } from '@/services/discord_service.js'
import { userService } from '@/services/user-service.js'
import { authService } from '@/services/auth-service.js'
import { userSocketContext } from '@/sockets/user-socket.js'
import { adminSocketContext } from '@/sockets/admin-socket.js'
import { navigator } from '@/router.js'


const userPrototype = {
  'id': '000174134145',
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
    userSocketStatus: 'disconnected',  // userSocket当前状态
    adminSocketStatus: 'disconnected',  // adminSocket当前状态
    enableAdminFunction: false,  // 启用管理员功能
  }),
  mutations: {
    // 设置当前用户
    setUserSocketStatus(state, status) {
      state.userSocketStatus = status
    },
    setAdminSocketStatus(state, status) {
      state.adminSocketStatus = status
    },
    setCurrentUser(state, data) {
      state.currentUser = data
    },
    setUserAvatar(state, obj) {
      state.userAvatar = obj
    },
    setUserAvatarURL(state, url) {
      state.userAvatar.url = url
    },
    setUserAvatarStatus(state, status) {
      state.userAvatar.status = status
    },
    setAdminFunctionStatus(state, status) {
      state.enableAdminFunction = status
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
    },

    // 加载用户头像数据
    async loadUserAvatar({ commit, getters }) {
      if (getters.userAvatarStatus === 'loading') {  // 判断当前头像获取状态
        return new Result(400, 'Avatar is still loading')
      }

      commit('setUserAvatarStatus', 'loading')
      const user = getters.currentUser

      if (user.avatar === null) {  // 判断用户头像hash有效性
        await commit('setUserAvatarStatus', 'unset')
        return new Result(404, 'Avatar not found')
      }

      // 获取用户头像
      const result = await discordService.fetchUserAvatar(user.id, user.avatar)
      if (result.isSuccess()) {  // 成功拉取用户头像信息
        globalEventbus.emit(Events.MITT.CURRENT_USER.AVATAR.LOAD_SUCCESS)  // 发布事件
        commit('setUserAvatarStatus', 'completed')
        commit('setUserAvatarURL', URL.createObjectURL(result.data))
      } else {  // 用户头像信息拉取失败
        globalEventbus.emit(Events.MITT.CURRENT_USER.AVATAR.LOAD_FAILED)
        commit('setUserAvatarStatus', 'unset')  // 变更状态
        commit('setUserAvatarURL', null)
      }
      return result
    },

    // 加载用户信息
    async loadCurrentUserDetails({ commit, dispatch }) {
      // 建立socketio连接到服务端
      // const result1 = await userSocketContext.connect()  // socketio连接建立失败
      // if (!result1.isSuccess()) return result1
      // 初始化用户信息
      const result = await userService.getUserDetails()
      if (result.code === 200) {
        // 成功拉取用户数据，将用户数据设置到vuex
        commit('setCurrentUser', result.data)
        dispatch('loadUserAvatar').then()  // 初始化用户头像
        dispatch('loadSystemInfo').then()  // 初始化服务器信息
      } else {  // 拉取用户信息失败
        // userSocketContext.disconnect()  // 断开socketio连接
      }
      return result
    },

    // 登出当前用户
    async logoutCurrentUser({ dispatch }) {
      const result = await authService.userLogout()
      if (result.isSuccess()) {  // 登出成功
        // await userSocketContext.disconnect()  // 断开user socket连接
        // await adminSocketContext.disconnect()  // 断开admin socket连接
        await dispatch('clearCurrentUser')  // 清除用户数据
        await dispatch('clearHistory')  // 清除用户历史
        await navigator.toLogin()  // 跳转到login页面
      } else {  // 登出失败
        globalEventbus.emit(Events.MITT.CURRENT_USER.LOGOUT.FAILED, result.message)
      }
    },

    setAdminFunctionStatus({ commit }, status) {
      commit('setAdminFunctionStatus', status)
    },

    upPrivilege() {
      // adminSocketContext.connect()  // 提权
    },
    downPrivilege() {
      // adminSocketContext.disconnect()  // 降权
    },
  },
  getters: {
    adminSocketStatus: state => state.adminSocketStatus,  // 管理员连接状态
    userSocketStatus: state => state.userSocketStatus,  // 用户连接当前状态
    userAvatarStatus: state => state.userAvatar.status,
    userAvatarURL: state => state.userAvatar.url,
    currentUser: state => state.currentUser,
    enableAdminFunction: state => state.enableAdminFunction
  },
}







