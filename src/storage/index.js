// noinspection JSIgnoredPromiseFromCall

import { createStore } from 'vuex'
import user from '@/storage/user-module.js'  // socket模块
import theme from '@/storage/theme-module.js'  // 主题模块
import locale from '@/storage/locale-module.js'  // 本地化模块
import server from '@/storage/server-module.js'  // 服务器信息模块
import atri from '@/storage/atri-module.js'  // 亚托莉模块
import history from '@/storage/history-module.js'  // 用户历史模块

const store = createStore({
  modules: {
    atri  /* 亚托莉模块 */,
    user  /* 用户模块 */,
    theme  /* 主题模块 */,
    locale  /* 语言模块 */,
    server  /* 后端模块 */,
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
