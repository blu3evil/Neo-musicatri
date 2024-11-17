// todo: 补齐主题定义
import baseStyle from '@/theme/base-theme.js'
import darkTheme from '@/theme/dark-theme.js'

/**
 * 主题定义，musicatri的主题直接使用js定义，并通过相关的js脚本对主题进行设置，使用时
 * 可直接定义js文件，并将其引入
 */
export const availableThemes = {
  'light': {
    name: 'Light Theme',
    styles: baseStyle
  },
  'dark': {
    name: 'Dark Theme',
    styles: darkTheme
  }
}

