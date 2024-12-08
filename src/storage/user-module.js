// socket-io模块
import { discordService } from '@/services/discord_service.js'
import { ToastMessage } from '@/utils/ui-helper.js'
import { i18n } from '@/locale/index.js'
import { config } from '@/config.js'
import { Events } from '@/sockets/events.js'
import { store } from '@/storage/index.js'
import { Result } from '@/common.js'

export default {
  namespace: true,
  state: () => ({
    currentUser: {
      'id': '000175',
      'avatar': null,
      'username': 'pineclone',
      'global_name': 'pineclone',
      'roles': ['anonymous'],
    },  // 当前用户(此处作占位)
    userSocketConnected: false,  // /socket/user命名空间socket连接是否建立
    adminSocketConnected: false, // /socket/admin命名空间socket连接是否建立

    userSocketStatus: 'vanilla',

    currentUserAvatarURL: null,  // 当前用户头像地址
    isAdminSocketConnecting: false,  // 当前是否正在建立到管理端的socketio连接
    isCurrentUserAvatarLoading: false,  // 当前用户头像是否正在加载
  }),
  mutations: {
    // 设置当前用户
    setUserSocketStatus(state, status) {
      state.userSocketStatus = status
    },
    setUserSocketConnectStatus(state, status) {
      state.userSocketConnected = status
    },
    setAdminSocketConnectStatus(state, status) {
      state.adminSocketConnected = status
    },
    setAdminSocketConnectingStatus(state, status) {
      state.isAdminSocketConnecting = status
    },
    setCurrentUser: (state, user) => {
      state.currentUser = user
    },
    setCurrentUserAvatarURL: (state, userAvatarURL) => {
      state.currentUserAvatarURL = userAvatarURL
    },
    setCurrentUserAvatarLoadingStatus(state, status) {
      state.isCurrentUserAvatarLoading = status
    }
  },
  actions: {
    setUserSocketStatus({ commit }, status) {
      commit('setUserSocketStatus', status)
    },

    // 设置当前用户
    setCurrentUser({ dispatch, commit }, user) {
      commit('setCurrentUser', user)  // 设置当前用户信息
      dispatch('initCurrentAvatar', user)  // 异步初始化用户头像
    },

    // 清除当前用户信息，用作登出或是socketio连接断开时
    clearCurrentUser({ commit }) {
      commit('setCurrentUser', null)  // 用户信息置空
      commit('setCurrentUserAvatarURL', null)  // 用户头像URL置空
    },

    async initCurrentUser({ dispatch, commit }) {
      const result = await new Promise(resolve => {
        // 给定超时，防止后端无响应
        let timeoutId = setTimeout(() => {
          ToastMessage.error(
            i18n.global.t('sockets.user-socket-client.fetch_user_timeout'),
          )
          resolve()
        }, config['REQUEST_TIMEOUT'])

        this.socket.emit(Events.CLIENT.USER.FETCH, async result => {
          if (result.code === 200) {
            // 成功拉取用户数据，将用户数据设置到vuex
            clearTimeout(timeoutId)
            await store.dispatch('setCurrentUser', result.data)
            await store.dispatch('setUserSocketConnectStatus', true)
            resolve(true) // 连接建立成功(阻塞)
          } else {
            // 拉取用户数据失败
            clearTimeout(timeoutId)
            ToastMessage.error(
              i18n.global.t('sockets.user-socket-client.fetch_user_error'),
            )
            resolve(false) // 拉取用户数据失败，连接建立失败
          }
        })
      })
    },

    initCurrentAvatar({ commit, getters }) {
      commit('setCurrentUserAvatarLoadingStatus', true)
      const user = getters.currentUser
      if (user.avatar === null) {  // 校验参数有效性
        return new Result(404, 'User Avatar URL Not Found')

        ToastMessage.error(i18n.global.t('storage.user-module.empty_avatar_url'))
        commit('setCurrentUserAvatarLoadingStatus', false)
        return
      }
      // 拉取用户头像
      discordService.fetchUserAvatar(user.id, user.avatar).then(result => {
        if (result.isSuccess()) {
          // 成功拉取用户头像信息
          const avatarURL = URL.createObjectURL(result.data)
          commit('setCurrentUserAvatarURL', avatarURL)
        } else {
          // 用户头像拉取失败
          ToastMessage.error(i18n.global.t('storage.user-module.fetch_user_avatar_failed'))
        }
        commit('setCurrentUserAvatarLoadingStatus', false)
      })
    },



    setUserSocketConnectStatus({ commit }, status) {
      commit('setUserSocketConnectStatus', status)
    },
    setAdminSocketConnectStatus({ commit }, status) {
      commit('setAdminSocketConnectStatus', status)
    },
    setAdminSocketConnectingStatus({ commit }, status) {
      commit('setAdminSocketConnectingStatus', status)
    }
  },
  getters: {
    userSocketStatus: state => state.userSocketStatus,  // 用户连接当前状态

    userSocketConnected: state => state.userSocketConnected,
    adminSocketConnected: state => state.adminSocketConnected,
    isAdminSocketConnecting: state => state.adminSocketConnected,  // 当前管理员socket是否正在连接
    currentUser: state => state.currentUser,
    currentUserAvatarURL: state => state.currentUserAvatarURL,
    isCurrentUserAvatarLoading: state => state.isCurrentUserAvatarLoading,
  },
}
