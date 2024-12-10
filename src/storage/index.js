// noinspection JSIgnoredPromiseFromCall

import { createStore } from 'vuex'
import user from '@/storage/user-module.js'  // socketio模块
import theme from '@/storage/theme-module.js'  // 主题模块
import locale from '@/storage/locale-module.js'
import history from '@/storage/history-module.js'

const store = createStore({
  modules: {
    user  /* 用户模块 */,
    theme  /* 主题模块 */,
    locale  /* 语言模块 */,
    history  /* 历史模块 */,
  },
})
// 监听状态变化同步到localStorage
store.subscribe((mutation, state) => {
  if (mutation.type === 'setActiveTheme') {  // 同步语言
    localStorage.setItem('activeTheme', state.theme.activeTheme)
  } else if (mutation.type === 'setActiveLanguage') {  // 同步主题
    localStorage.setItem('activeLanguage', state.locale.activeLanguage)
  }
})
store.dispatch('loadActiveTheme')
store.dispatch('loadActiveLanguage')  // 加载默认主题
export { store }
