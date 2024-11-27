// noinspection JSIgnoredPromiseFromCall

import { createStore } from 'vuex'
import theme from '@/storage/theme-module.js'  // 主题模块
import socket from '@/storage/socket-module.js'  // socketio模块
import locale from '@/storage/locale-module.js'

import axios from 'axios'
const availableSettingPages = ['appearance', 'profile']  // 可用设置页面列表

const store = createStore({
  modules: {
    theme  /* 主题模块 */,
    socket  /* socketio模块 */,
    locale  /* 本地化模块 */,
  },
  state: {
    activeSettingPage: 'appearance',    // 当前激活的设置页面
    pathBeforeIntoSettingPage: '',      // 进入设置页面之前所在页面，用于从设置页面回溯
    config: null,                       // 项目配置
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
    async loadConfig({ state, commit }) {
      // 避免重复初始化配置
      if (state.config === null) {
        const response = await axios.get('/config.json')
        commit('setConfig', response.data)
      }
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
    // 同步设置页面
    localStorage.setItem('activeSettingPage', state.activeSettingPage)
  } else if (mutation.type === 'setActiveTheme') {
    // 同步主题，此处应当使用模块引用
    localStorage.setItem('activeTheme', state.theme.activeTheme)
  } else if (mutation.type === 'setActiveLanguage') {
    // 同步语言
    localStorage.setItem('activeLanguage', state.locale.activeLanguage)
  }
})

store.dispatch('loadActiveSettingPage') // 加载activeSettingPage
store.dispatch('loadConfig')  // 加载config
store.dispatch('loadActiveTheme')
// store.dispatch('loadActiveLanguage')  // 加载默认主题
store.dispatch('initI18n')
export { store }
