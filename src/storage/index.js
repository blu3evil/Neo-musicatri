// noinspection JSIgnoredPromiseFromCall

import { createStore } from 'vuex'
import axios from 'axios'

// todo: 可能将axios逻辑优化到vuex
const availableSettingPages = ['appearance', 'profile']  // 可用设置页面列表

const store = createStore({
  state: {
    activeSettingPage: 'appearance', // 当前激活的设置页面
    pathBeforeIntoSettingPage: '',  // 进入设置页面之前所在页面，用于从设置页面回溯
    accessToken: null,  // access token
    isAuthenticated: false,  // 当前是否已经验证
    config: null,  // 项目配置
    deviceId: null  // 设备id，用于区分浏览器和多设备
  },
  mutations: {
    // Setter
    setActiveSettingPage(state, activeSettingPage) {
      state.activeSettingPage = activeSettingPage
    },
    setPathBeforeIntoSettingPage(state, pathBeforeIntoSettingPage) {
      state.pathBeforeIntoSettingPage = pathBeforeIntoSettingPage
    },
    // 设置access token
    setAccessToken(state, payload) {
      state.accessToken = payload  // 设置access token
    },
    // 清除access token
    clearAccessToken(state) {
      state.accessToken = null
      state.isAuthenticated = false
    },
    setConfig(state, config) {
      state.config = config
    },

    setDeviceId(state, deviceId) {
      state.deviceId = deviceId
    }
  },
  actions: {
    // 加载activeSettingPage
    loadActiveSettingPage({ commit }) {
      let localstorageActiveSettingPage = localStorage.getItem('activeSettingPage')
      let flag = localstorageActiveSettingPage != null
        && availableSettingPages.includes(localstorageActiveSettingPage)

      if (flag) commit('setActiveSettingPage', localstorageActiveSettingPage)
      else commit('setActiveSettingPage', availableSettingPages[0])
    },

    // 加载AccessToken
    loadAccessToken({ commit }) {
      let localstorageAccessToken = localStorage.getItem('accessToken')
      commit('setAccessToken', localstorageAccessToken)
    },
    // 异步处理access_token以及expires_in
    setAccessToken({ commit }, access_token) {
      commit('setAccessToken', access_token)
    },
    clearAccessToken({ commit }) {
      commit('clearAccessToken')
    },
    // 加载项目配置
    loadConfig({ commit }) {
      axios.get('/config.json')
        .then(data => commit('setConfig', data.data))
        .catch(error => console.log(error))
    },
    // 加载设备id
    loadDeviceId({ commit }) {
      let localstorageDeviceId = localStorage.getItem('deviceId')
      if (localstorageDeviceId == null) {
        // deviceId为空，生成新的deviceId
        let deviceId =  crypto.randomUUID()
        commit('setDeviceId', deviceId)
      } else {
        // deviceId不为空，直接使用
        commit('setDeviceId', localstorageDeviceId)
      }
    }
  },
  getters: {
    // activeSettingPage GETTER
    activeSettingPage: state => state.activeSettingPage,
    pathBeforeIntoSettingPage: state => state.pathBeforeIntoSettingPage,
    accessToken: state => state.accessToken,  // access token
    config: state => state.config,  // config
    deviceId: state => state.deviceId  // deviceId
  }
})

// 监听状态变化，将其同步到 localStorage
store.subscribe((mutation, state) => {
  // 数据监听，变化时自动同步到localstorage
  if (mutation.type === 'setActiveSettingPage') {
    localStorage.setItem('activeSettingPage', state.activeSettingPage)
  }

  if (mutation.type === 'setAccessToken') {
    // 将access token同步到localstorage
    localStorage.setItem('accessToken', state.accessToken)
  }

  if (mutation.type === 'setDeviceId') {
    // 将deviceId同步到localstorage
    localStorage.setItem('deviceId', state.deviceId)
  }
})

store.dispatch('loadActiveSettingPage') // 加载activeSettingPage
store.dispatch('loadAccessToken') // 加载access_token
store.dispatch('loadConfig')  // 加载config
store.dispatch('loadDeviceId')  // 加载deviceId

export default store
