// noinspection JSIgnoredPromiseFromCall

import { createStore } from 'vuex'
import axios from 'axios'
// todo: 可能将axios逻辑优化到vuex
const availableSettingPages = ['appearance', 'profile']  // 可用设置页面列表

const store = createStore({
  modules: {
  },
  state: {
    activeSettingPage: 'appearance',    // 当前激活的设置页面
    pathBeforeIntoSettingPage: '',      // 进入设置页面之前所在页面，用于从设置页面回溯
    config: null                       // 项目配置
  },
  mutations: {
    // Setter
    setActiveSettingPage(state, activeSettingPage) {
      state.activeSettingPage = activeSettingPage
    },
    setPathBeforeIntoSettingPage(state, pathBeforeIntoSettingPage) {
      state.pathBeforeIntoSettingPage = pathBeforeIntoSettingPage
    },

    setConfig(state, config) {
      state.config = config
    },

    setDeviceId(state, deviceId) {
      state.deviceId = deviceId
    },
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
    // 加载项目配置
    async loadConfig({ commit }) {
      const response = await axios.get('/config.json')
      commit('setConfig', response.data)
    },
  },
  getters: {
    // activeSettingPage GETTER
    activeSettingPage: state => state.activeSettingPage,
    pathBeforeIntoSettingPage: state => state.pathBeforeIntoSettingPage,
    config: state => state.config,  // config
  }
})

// 监听状态变化，将其同步到 localStorage
store.subscribe((mutation, state) => {
  // 数据监听，变化时自动同步到localstorage
  if (mutation.type === 'setActiveSettingPage') {
    localStorage.setItem('activeSettingPage', state.activeSettingPage)
  }
})

store.dispatch('loadActiveSettingPage') // 加载activeSettingPage
store.dispatch('loadConfig')  // 加载config


export default store
