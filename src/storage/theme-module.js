// 主题模块
import { availableThemes } from '@/theme/index.js'

export default {
  namespace: true,
  state: () => ({
    activeTheme: localStorage.getItem('activeTheme'),
  }),
  mutations: {
    // 变更主题状态
    setActiveTheme(state, theme) {
      state.activeTheme = theme
    }
  },
  actions: {
    // 设置激活主题
    setActiveTheme({ commit }, theme) {
      if (availableThemes[theme]) {
        // 主题存在，设置主题
        const style = availableThemes[theme]['styles']
        for (let key in style) {  // 遍历主题字段逐个设置
          document.documentElement.style.setProperty(key, style[key])
        }
        // 变更状态
        commit('setActiveTheme', theme)
      }
    },
    // 初始化激活主题
    loadActiveTheme({ commit, dispatch }) {
      // 通过localstorage加载主题
      let localstorageTheme = localStorage.getItem('activeTheme')

      // localstorage主题存在直接使用localstorage主题
      if (availableThemes[localstorageTheme]) {
        dispatch('setActiveTheme', localstorageTheme)  // 使用localstorage设置主题
        return
      }
      // 媒体查询主题
      const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)')
      const mediaTheme = darkModeQuery.matches ? 'dark' : 'light'

      // 使用媒体查询主题作为第二主题
      if (availableThemes[mediaTheme]) {
        dispatch('setActiveTheme', mediaTheme)  // 使用localstorage设置主题
        return
      }
      // 没有命中目标主题，默认使用亮色主题
      dispatch('setActiveTheme', 'light')
    }
  },
  getters: {
    activeTheme: state => state.activeTheme,
  },
}

