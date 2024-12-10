import zh_CN from './zh-CN.js'
import en_US from './en-US.js'
import { createI18n } from 'vue-i18n'

export const availableLanguages = {
  'en-US': {
    name: 'English(US)',
    locale: en_US,
  },
  'zh-CN': {
    name: '简体中文',
    locale: zh_CN,
  }
}

const messages = {}
Object.keys(availableLanguages).forEach((lang) => {
  messages[lang] = availableLanguages[lang].locale
})

export let i18n = null
export const initI18n = (activeLanguage) => {
  i18n = createI18n({
    legacy: false,
    locale: activeLanguage,
    messages: messages
  })
  return i18n
}





