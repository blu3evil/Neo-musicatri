// todo: 补齐主题定义
import { darkTheme } from '@/theme/dark-theme.js'
import { baseStyle } from '@/theme/base-theme.js'

/**
 * 主题定义，musicatri的主题直接使用js定义，并通过相关的js脚本对主题进行设置，使用时
 * 可直接定义js文件，并将其引入
 */
const themes = {}

/**
 * 创建主题方法
 * @param id 主题id
 * @param name 主题名称
 * @param style 主题定义，通过键值对的形式定义css样式
 */
const registerTheme = (id, name, style) => {
  // 使用themeDefinition来覆盖默认的样式表
  themes[id] = {
    id: id,
    name: name,
    style: {
      ...baseStyle,
      ...style,
    }
  }
}
const localstorageTag = 'activeTheme'
/**
 * 初始化主题设置
 */
const initTheme = () => {
  // 注册主题
  registerTheme(0, '☀️light', {})  // 亮色主题
  registerTheme(1, '🌙dark', darkTheme)  // 暗色主题
  setTheme(getActiveThemeId())  // 查询获取默认的主题并设置
}

/**
 * 设置应用主题
 * @param themeId 主题名称，参考{@link themes}键名定义
 */
const setTheme = (themeId) => {
  if (themeId == null) return false  // themeId为null，不执行修改

  let targetTheme = themes[themeId]
  if (targetTheme !== -1) {  // 检查是否存在指定id的主题
    // 主题存在，设置主题
    localStorage.setItem(localstorageTag, themeId)  // 将默认主题设置进入localstorage
    let styleDefinition = targetTheme['style']
    for (let key in styleDefinition) {  // 遍历主题字段逐个设置
      document.documentElement.style.setProperty(key, styleDefinition[key])
    }
    return true  // 修改成功
  }
  return false  // 没有修改
}

/**
 * 获取主题集合
 * @returns {{}} 主题集合
 */
const getThemes = () => {
  return themes
}

/**
 * 取得当前主题，默认从localstorage中尝试获取，如果没有获取，那么执行媒体查询后获取主题返回，
 * 同时再次将媒体查询结果主题存储进入localstorage
 */
const getActiveThemeId = () => {
  let activeThemeId

  // 检查用户媒体类型
  const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const mediaThemeId = darkModeQuery.matches ? 1 : 0

  // 校验localstorage参数合法性
  let localstorageThemeId = localStorage.getItem(localstorageTag)
  let flag1 = (localstorageThemeId === null)  // 判空
  let flag2 = isNaN(Number(localstorageThemeId))  // 非数字

  if (flag1 || flag2) {
    // localstorageId参数非法，使用媒体查询主题，并且将媒体查询主题设置进入localstorageId
    activeThemeId = mediaThemeId
    localStorage.setItem(localstorageTag, String(mediaThemeId))
  } else {
    // localstorageId参数合法，直接使用localstorageId
    activeThemeId = localstorageThemeId
  }
  return Number(activeThemeId)  // 返回当前主题名称
}

export {
  setTheme,  // 设置主题
  initTheme,  // 初始化主题
  getActiveThemeId,  // 获得当前主题名称
  getThemes,
}
