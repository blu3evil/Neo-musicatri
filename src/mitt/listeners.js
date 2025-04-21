import { globalEventbus } from '@/mitt/global-eventbus.js'
import { ToastMessage } from '@/utils/ui-helper.js'
import { Events } from '@/events.js'
import { i18n } from '@/locale/index.js'
import { store } from '@/storage/index.js'

// 用户头像拉取失败
globalEventbus.on(Events.MITT.CURRENT_USER.AVATAR.LOAD_FAILED, () => {
  ToastMessage.error(i18n.global.t('component.user-avatar.fetch_avatar_failed'))
})

// 服务器信息拉取失败
globalEventbus.on(Events.MITT.SYSTEM_INFO.LOAD_FAILED, () => {
  ToastMessage.error(i18n.global.t('utils.ui-helper.system_info_load_failed'))
})

// 用户登出失败
globalEventbus.on(Events.MITT.CURRENT_USER.LOGOUT.FAILED, message => {
  ToastMessage.error(message)
})

// 管理员功能开启成功
globalEventbus.on(Events.MITT.ADMIN_FUNCTION.ENABLE.SUCCESS, () => {
  ToastMessage.success(i18n.global.t('view.AboutSetting.admin_function_enable_success'))
})

// 管理员功能开启失败
globalEventbus.on(Events.MITT.ADMIN_FUNCTION.ENABLE.FAILED, reason => {
  ToastMessage.error(i18n.global.t('view.AboutSetting.admin_function_enable_failed', { reason }))
})

// 管理员功能关闭成功
globalEventbus.on(Events.MITT.ADMIN_FUNCTION.DISABLE.SUCCESS, async () => {
  let workspaceHistory = store.getters.history.workspaceHistory
  if (!['portal'].includes(workspaceHistory)) {
    await store.dispatch('setHistory', {
      name: 'workspaceHistory', history: 'portal'
    })  // 若workspace路径处于非一般页面那么重置历史到portal
  }
  ToastMessage.success(i18n.global.t('view.AboutSetting.admin_function_disable_success'))
})

// 管理员功能关闭失败
globalEventbus.on(Events.MITT.ADMIN_FUNCTION.DISABLE.FAILED, reason => {
  ToastMessage.error(i18n.global.t('view.AboutSetting.admin_function_disable_failed', { reason }))
})

// 用户数据成功修改
globalEventbus.on(Events.MITT.USER.DATA.PATCH.SUCCESS, globalName => {
  ToastMessage.success(i18n.global.t('view.workspace.UserManagement.submit_change_success', { globalName }))
})

// 删除用户
globalEventbus.on(Events.MITT.USER.DELETE.FAILED, ({ globalName, reason }) => {
  ToastMessage.error(i18n.global.t('view.workspace.UserManagement.delete_user_failed', { globalName, reason }))
})

globalEventbus.on(Events.MITT.USER.DELETE.SUCCESS, ({ globalName }) => {
  ToastMessage.success(i18n.global.t('view.workspace.UserManagement.delete_user_success', { globalName }))
})



