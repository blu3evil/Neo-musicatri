import { i18n } from '@/locale/index.js'
import { ElNotification } from 'element-plus'
import { ElMessageBox } from 'element-plus'

export class PopupMessage {
  static warning(
    message,
    title=i18n.global.t('utils.ui-helper.popup_message_warning_title'),
    confirmButtonText=i18n.global.t('utils.ui-helper.popup_message_warning_confirm'),
    cancelButtonText=i18n.global.t('utils.ui-helper.popup_message_warning_cancel'),
  ) {
    return ElMessageBox.confirm(
      message,
      title,
      {
        confirmButtonText,
        cancelButtonText,
        type: 'warning',
        customClass: 'popup-message',
      }
    )
  }
}

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
