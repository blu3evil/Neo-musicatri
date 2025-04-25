// noinspection JSIgnoredPromiseFromCall

import { createStore } from 'vuex'
import user from '@/storage/user-module.js'  // 用户模块
import auth from '@/storage/auth-module.js'  // 认证模块
import atri from '@/storage/atri-module.js'  // 亚托莉模块
import theme from '@/storage/theme-module.js'  // 主题模块
import locale from '@/storage/locale-module.js'  // 本地化模块
import server from '@/storage/server-module.js'  // 服务器信息模块
import history from '@/storage/history-module.js'  // 用户历史模块

const store = createStore({
  modules: {
    atri  /* 亚托莉模块 */,
    auth  /* 认证模块 */,
    user  /* 用户模块 */,
    theme  /* 主题模块 */,
    locale  /* 语言模块 */,
    server  /* 后端模块 */,
    history  /* 历史模块 */,
  },
})
// 监听状态变化同步到localStorage
store.subscribe((mutation, state) => {
  switch (mutation.type) {
    case 'setActiveLanguage':
      localStorage.setItem('activeLanguage', state.locale.activeLanguage); break
    case 'setActiveTheme':
      localStorage.setItem('activeTheme', state.theme.activeTheme); break
    case 'setAccessToken':
      localStorage.setItem('accessToken', state.auth.accessToken); break
    case 'setExpiresAt':
      localStorage.setItem('expiresAt', state.auth.expiresAt); break
    case 'setTokenType':
      localStorage.setItem('tokenType', state.auth.tokenType); break
  }
})
store.dispatch('loadActiveTheme')
store.dispatch('loadActiveLanguage')  // 加载 默认主题
store.dispatch('loadAuthToken')  // 加载登录凭证
export { store }
