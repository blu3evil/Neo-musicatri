// noinspection JSUnresolvedReference

import { config } from '@/config.js'
import { i18n } from '@/locale/index.js'
import { Events } from '@/events.js'
import { ToastMessage } from '@/utils/ui-helper.js'
import { SocketContext } from '@/sockets/socket-context.js'
import { store } from '@/storage/index.js'

class AdminSocketContext extends SocketContext {
  constructor() {
    super(
      `${config['SOCKET_ENDPOINT']}/admin`, config['SOCKET_CONNECT_TIMEOUT'],
    )
  }

  preInitialize() {
    // 管理员socketio状态改变
    this.eventbus.on(Events.MITT.SOCKET_CONTEXT.STATE.CHANGE, async (identify) => {
      await store.dispatch('setAdminSocketStatus', identify)
    })

    // 管理员socketio连接成功
    this.eventbus.on(Events.MITT.SOCKET_CONTEXT.CONNECT.SUCCESS, () => {
      ToastMessage.success(i18n.global.t('sockets.admin-socket.connect_success'))
    })

    // 管理员socketio连接失败
    this.eventbus.on(Events.MITT.SOCKET_CONTEXT.CONNECT.FAILED, reason => {
      ToastMessage.error(i18n.global.t('sockets.admin-socket.connect_failed', { reason }))
    })

    // 管理员socketio断开超时
    this.eventbus.on(Events.MITT.SOCKET_CONTEXT.DISCONNECT.FAILED, reason => {
      ToastMessage.error(i18n.global.t('sockets.admin-socket.disconnect_timeout'), { reason })
    })

    // 管理员socketio断开连接
    this.eventbus.on(Events.MITT.SOCKET_CONTEXT.DISCONNECT.FORCE, () => {
      ToastMessage.error(i18n.global.t('sockets.admin-socket.connect_shutdown'))
    })

    this.eventbus.on(Events.MITT.SOCKET_CONTEXT.DISCONNECT.SUCCESS, () => {
      ToastMessage.success(i18n.global.t('sockets.admin-socket.disconnect_success'))
    })

    this.on(Events.SOCKETIO.ATRI.STATE.CHANGE, identify => {
      ToastMessage.info(i18n.global.t('sockets.admin-socket.atri_state_change', { identify }))
    })
  }
}

export const adminSocketContext = new AdminSocketContext()
