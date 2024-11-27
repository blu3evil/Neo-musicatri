import { availableLanguages } from '@/locale/index.js'
import { createI18n } from 'vue-i18n'
const localstorageTag = 'activeLanguage'

function validateLanguage(language) {
  const validLanguage = availableLanguages[language]
  return validLanguage !== undefined && availableLanguages[language] !== null
}

const messages = {}
Object.keys(availableLanguages).forEach((lang) => {
  messages[lang] = availableLanguages[lang].locale
})

export default {
  namespace: true,
  state: () => ({
    activeLanguage: null,
    i18n: null,
  }),
  mutations: {
    // 变更当前语言
    setActiveLanguage(state, language) {
      state.activeLanguage = language
    },
    setI18n(state, i18n) {
      state.i18n = i18n
    }
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
    async initI18n({ getters, commit, dispatch }) {
      await dispatch('loadActiveLanguage')
      const i18n = createI18n({
        legacy: false,
        locale: getters.activeLanguage,
        messages: messages
      })
      commit('setI18n', i18n)
    }
  },
  getters: {
    activeLanguage: state => state.activeLanguage,
    i18n: state => state.i18n
  },
}

