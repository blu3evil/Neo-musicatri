import { availableLanguages } from '@/locale/index.js'
const localstorageTag = 'activeLanguage'

function validateLanguage(language) {
  const validLanguage = availableLanguages[language]
  return validLanguage !== undefined && availableLanguages[language] !== null
}

export default {
  namespace: true,
  state: () => ({
    activeLanguage: null,
  }),
  mutations: {
    // 变更当前语言
    setActiveLanguage(state, language) {
      state.activeLanguage = language
    },
  },
  actions: {
    setActiveLanguage({ commit }, language) {
      if (validateLanguage(language)) {
        commit('setActiveLanguage', language)
        return true
      }
      return false
    },
    // 初始化激活主题
    async loadActiveLanguage({ dispatch }) {
      // localstorage存储语言
      const localstorageLang = localStorage.getItem(localstorageTag);
      if (await dispatch('setActiveLanguage', localstorageLang)) return

      // 用户浏览器语言
      const navigatorLang = navigator.language || navigator.userLanguage;  // 获取用户语言
      if (await dispatch('setActiveLanguage', navigatorLang)) return

      // 未找到可用语言，使用英文作为默认语言
      if (!await dispatch('setActiveLanguage', 'en-US')) {
        console.log('language initialize failed')
      }
    },
  },
  getters: {
    activeLanguage: state => state.activeLanguage,
  },
}

