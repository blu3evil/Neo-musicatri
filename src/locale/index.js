// 本地化
import { createI18n } from 'vue-i18n'
import zh_CN from './zh-CN.js'
import en_US from './en-US.js'


const localstorageTag = 'activeLanguage'
const messages = {
  'zh-CN': zh_CN,
  'en-US': en_US,
}

const displayNames = {
  'zh-CN': 'Chinese(Simplify)',
  'en-US': 'English(US)',
}

const availableLanguages = []
for (const key in messages) {
  availableLanguages.push(key)
}

/**
 * 返回当前的语言文件类型，例如en-US, zh-CN
 */
const getActiveLanguage = () => {
  // localstorage存储语言
  const localstorageLang = localStorage.getItem(localstorageTag);
  if (availableLanguages.indexOf(localstorageLang) !== -1) {
    // 语言列表存在localstorageLang
    return localstorageLang
  }

  // 用户浏览器语言
  const navigatorLang = navigator.language || navigator.userLanguage;  // 获取用户语言
  if (availableLanguages.indexOf(navigatorLang) !== -1) {
    // 用户浏览器语言存在列表中，重置localstorage存储语言
    localStorage.setItem(localstorageTag, navigatorLang)
    return navigatorLang
  }

  // 未找到可用语言，使用英文作为默认语言
  localStorage.setItem(localstorageTag, 'en-US')
  return 'en-US';
}

/**
 * 获取语言显示名称，例如'English(US)'
 * @param lang 语言类型，例如'en-US'
 * @returns {*|string}
 */
const getLanguageDisplayName = (lang) => {
  return displayNames[lang] || 'unknown'
}

const initI18n = () => {
  return createI18n({
    // 优先选择用户本地语言
    // globalInjection: true,  // 全局生效$t
    legacy: false,
    locale: getActiveLanguage(),
    messages: messages
  })
}

// 可用语言列表
export {
  initI18n,
  availableLanguages,
  getActiveLanguage,
  getLanguageDisplayName,
  localstorageTag
};

