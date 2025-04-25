import { Result } from '@/common.js'
import { globalEventbus } from '@/mitt/global-eventbus.js'
import { Events } from '@/events.js'
import { discordService } from '@/services/discord_service.js'
import { userServiceV1 } from '@/services/user-service-v1.js'
import { authServiceV1 } from '@/services/auth-service.js'
// import { userSocketContext } from '@/sockets/user-socket.js'
// import { adminSocketContext } from '@/sockets/admin-socket.js'
import { navigator } from '@/router.js'
import { AvatarStatus } from '@/status.js'

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
    currentUser: userPrototype, // 当前用户(此处作占位)
    userAvatar: userAvatarPrototype, // 当前用户头像

    userAvatarContexts: {},  /* 用户头像上下文，存储用户头像相关状态量 */

    userSocketStatus: 'disconnected', // userSocket当前状态
    adminSocketStatus: 'disconnected', // adminSocket当前状态
    enableAdminFunction: false, // 启用管理员功能
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
    setAdminFunctionStatus(state, status) {
      state.enableAdminFunction = status
    },
    setAvatarHash(state, { id, avatar }) {
      state.userAvatarContexts[id].avatar = avatar
    },
    setAvatarStatus(state, { id, status }) {
      state.userAvatarContexts[id].status = status // 设置某一个用户的Avatar状态
    },
    setAvatarURL(state, { id, url }) {
      state.userAvatarContexts[id].url = url // 设置某一个用户的Avatar路径
    },
    clearCurrentUser(state) {
      state.currentUser = userPrototype
    },
    clearAvatarContext(state, { id }) {  // 清理某个用户的头像上下文，登出时使用
      state.userAvatarContexts[id] = null
    }
  },
  actions: {
    setUserSocketStatus({ commit }, status) {
      commit('setUserSocketStatus', status)
    },
    setAdminSocketStatus({ commit }, status) {
      commit('setAdminSocketStatus', status)
    },
    // 清除当前用户数据，在用户登出的时候使用
    clearCurrentUser({ commit, getters }) {
      const user_id = getters.currentUser.id
      commit('clearCurrentUser')  // 清理当前用户
      commit('clearAvatarContext', { id: user_id })  // 清理用户头像
    },

    /**
     * 预加载头像数据，主要是填充头像hash，之后通过{@link loadAvatar}实际加载用户头像数据
     * @return Promise<Result>
     */
    async prepareAvatar({ commit, getters }, { id, avatar }) {
      // commit('ensureAvatarContext', { id })

      // 判断用户头像hash有效性
      if (avatar === null) {
        return new Result(404, 'Avatar not found')
      }

      // 头像hash重复，避免重复加载
      if (getters.safeUserAvatarContexts(id).avatar === avatar) {  //
        return new Result(200, 'Duplicate avatar hash was supplied, operation will be ignored.')
      }

      commit('setAvatarHash', { id, avatar })  // 设置头像hash
      commit('setAvatarStatus', { id, status: AvatarStatus.PREPARED })
      return new Result(200, `Success upload avatar hash to user ${id}`)
    },

    /**
     * 指定加载用户头像数据，如果没有传入avatar hash，那么使用上一次的avatar hash加载用户头像
     * @return Promise<Result>
     */
    async loadAvatar({ commit, getters }, { id }) {
      // commit('ensureAvatarContext', { id })
      let currentStatus = getters.safeUserAvatarContexts(id).status

      // 检查是否可以加载
      if (![AvatarStatus.PREPARED,AvatarStatus.FAILED].includes(currentStatus)) {
        return new Result(400, 'Avatar is not allow to load')
      }

      // 检查是否已经加载完成，避免重复加载
      if ([AvatarStatus.COMPLETED].includes(currentStatus)) {
        return new Result(200, 'Avatar have already done loading')
      }

      let avatar =  getters.safeUserAvatarContexts(id).avatar
      commit('setAvatarStatus', { id, status: AvatarStatus.LOADING }) // 将状态设置为loading
      const result = await discordService.fetchUserAvatar(id, avatar) // 加载头像
      if (result.isSuccess()) {
        commit('setAvatarURL', { id, url: URL.createObjectURL(result.data) })
        commit('setAvatarStatus', { id, status: AvatarStatus.COMPLETED })
      } else {
        commit('setAvatarStatus', { id, status: AvatarStatus.FAILED }) // 变更状态
      }
      return result
    },

    // 加载用户信息
    async loadCurrentUserDetails({ commit, dispatch }) {
      // 建立socketio连接到服务端
      // const result1 = await userSocketContext.connect()  // socketio连接建立失败
      // if (!result1.isSuccess()) return result1
      // 初始化用户信息
      const result = await userServiceV1.getCurrentUserDetails()
      // console.log(result)

      if (result.code === 200) {
        // 成功拉取用户数据，将用户数据设置到vuex
        let currentUser = result.data
        commit('setCurrentUser', currentUser)

        // 加载当前用户头像
        // 准备当前用户头像数据
        dispatch('prepareAvatar', {
          id: currentUser.id,
          avatar: currentUser.avatar,
        }).then()
        dispatch('loadAvatar', { id: currentUser.id }).then(result => {
          if (!result.isSuccess()) {
            // 用户头像加载失败
            globalEventbus.emit(Events.MITT.CURRENT_USER.AVATAR.LOAD_FAILED)
          } else {
            // 用户头像加载成功
            globalEventbus.emit(Events.MITT.CURRENT_USER.AVATAR.LOAD_SUCCESS)
          }
        })

        // 加载服务端数据
        dispatch('loadSystemInfo').then() // 初始化服务器信息
      } else {
        // 拉取用户信息失败
        // userSocketContext.disconnect()  // 断开socketio连接
      }
      return result
    },

    // 登出当前用户
    async logoutCurrentUser({ dispatch }) {
      const result = await authServiceV1.userLogout()
      if (result.isSuccess()) {
        // 登出成功
        // await userSocketContext.disconnect()  // 断开user socket连接
        // await adminSocketContext.disconnect()  // 断开admin socket连接
        await dispatch('clearCurrentUser') // 清除用户数据
        await dispatch('clearHistory') // 清除用户历史
        await navigator.toLogin() // 跳转到login页面
      } else {
        // 登出失败
        globalEventbus.emit(
          Events.MITT.CURRENT_USER.LOGOUT.FAILED,
          result.message,
        )
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
    adminSocketStatus: state => state.adminSocketStatus, // 管理员连接状态
    userSocketStatus: state => state.userSocketStatus, // 用户连接当前状态
    userAvatarStatus: state => state.userAvatar.status,
    userAvatarURL: state => state.userAvatar.url,
    currentUser: state => state.currentUser,
    enableAdminFunction: state => state.enableAdminFunction,
    // userAvatarContexts: state => state.userAvatarContexts,
    safeUserAvatarContexts: state => (id) => {
      if (!state.userAvatarContexts[id]) {
        state.userAvatarContexts[id] = {
          id: id,  /* 用户id */
          url: '',  /* 头像链接 */
          avatar: '',  /* 头像hash */
          status: 'idle',  /* 当前头像状态 */
        }
      }
      return state.userAvatarContexts[id]
    },
  },
}







