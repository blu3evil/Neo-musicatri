// noinspection JSUnresolvedReference

import { config } from '@/config.js'
import { Events } from '@/events.js'
import { SocketContext } from '@/sockets/socket-context.js'
import { ToastMessage } from '@/utils/ui-helper.js'
import { i18n } from '@/locale/index.js'
import { store } from '@/storage/index.js'

class UserSocketContext extends SocketContext {
  constructor() {
    super(`${config['SOCKET_ENDPOINT']}/user`, config['SOCKET_CONNECT_TIMEOUT'])
  }

  preInitialize() {
    // 用户socketio状态改变
    this.eventbus.on(Events.MITT.SOCKET_CONTEXT.STATE.CHANGE, async (identify) => {
      await store.dispatch('setUserSocketStatus', identify)
    })

    // 用户socketio断开失败
    this.eventbus.on(Events.MITT.SOCKET_CONTEXT.DISCONNECT.FAILED, (reason) => {
      ToastMessage.error(i18n.global.t('sockets.user-socket.connect_shutdown'), {reason})
    })

    // 用户socketio断开连接
    this.eventbus.on(Events.MITT.SOCKET_CONTEXT.DISCONNECT.FORCE, () => {
      ToastMessage.error(i18n.global.t('sockets.user-socket.connect_shutdown'))
    })
  }
}

export const userSocketContext = new UserSocketContext()
