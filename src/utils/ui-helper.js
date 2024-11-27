import { ElNotification } from 'element-plus'
import { store } from '@/storage/index.js'

const i18n = store.getters.i18n

class ToastMessage {
  static success() {
    ElNotification({  // 弹出提示
      title: i18n.global.t('sockets.socket-client.socket_error_title'),
      message: i18n.global.t('sockets.socket-client.socket_connect_error_message'),
      position: 'bottom-right',
    })
  }
}
