import { ElNotification } from 'element-plus'
import { i18n } from '@/locale/index.js'

export class ToastMessage {
  // 成功
  static success(message) {
    ElNotification({  // 弹出提示
      title: i18n.global.t('utils.ui-helper.toast_message_success_title'),
      message: message,
      position: 'bottom-right',
    })
  }
  // 错误
  static error(message) {
    ElNotification({  // 弹出提示
      title: i18n.global.t('utils.ui-helper.toast_message_error_title'),
      message: message,
      position: 'bottom-right',
    })
  }
  // 提示
  static info(message) {
    ElNotification({
      title: i18n.global.t('utils.ui-helper.toast_message_info_title'),
      message: message,
      position: 'bottom-right',
    })
  }
  // 警告
  static warning(message) {
    ElNotification({
      title: i18n.global.t('utils.ui-helper.toast_message_warning_title'),
      message: message,
      position: 'bottom-right',
    })
  }
}
