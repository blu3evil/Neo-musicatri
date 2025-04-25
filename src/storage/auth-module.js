import { availableThemes } from '@/theme/index.js'

export default {
  namespace: true,
  state: () => ({
    accessToken: null,
    expiresAt: localStorage.getItem("expiresAt"),
    tokenType: localStorage.getItem("tokenType"),
  }),
  mutations: {
    setAccessToken: (state, accessToken) => {
      state.accessToken = accessToken
    },
    setExpiresAt: (state, expiresAt) => {
      state.expiresAt = expiresAt
    },
    setTokenType(state, tokenType) {
      state.tokenType = tokenType
    }
  },
  actions: {
    // 认证成功后使用此action
    storeAuthToken({ commit }, {accessToken, expiresAt, tokenType }) {
      commit('setAccessToken', accessToken)
      commit('setExpiresAt', expiresAt)
      commit('setTokenType', tokenType)
    },
    // 加载authToken，此方法从localstorage中加载持久化存储的登录凭证信息
    loadAuthToken({ commit }) {
      // 通过localstorage加载主题
      commit('setTokenType', localStorage.getItem("tokenType"))
      commit('setExpiresAt', localStorage.getItem("expiresAt"))
      commit('setAccessToken', localStorage.getItem("accessToken"))
    }
  },
  getters: {
    accessToken: state => state.accessToken,
    // 拼接tokenType、AccessToken，构建jwt请求头
    authorizationHeader(state) {
      if (!state.accessToken
        || !state.expiresAt
        || !state.tokenType
        || new Date().getTime() > state.expiresAt * 1000) {
        // accessToken相关参数为空，或已经过期
        return null
      }
      return `${state.tokenType} ${state.accessToken}`
    },
  },
}
