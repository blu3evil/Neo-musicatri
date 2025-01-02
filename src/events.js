export const Events = {
  // mitt事件
  MITT: {
    CURRENT_USER: {
      AVATAR: {
        LOAD_SUCCESS: "mitt:current_user:avatar:load_success",
        LOAD_FAILED: "mitt:current_user:avatar:load_failed"
      },
      LOGOUT: {
        FAILED: "mitt:current_user:logout:failed"
      }
    },
    SYSTEM_INFO: {
      LOAD_SUCCESS: "mitt:system_info:load_success",
      LOAD_FAILED: "mitt:system_info:load_failed"
    },
    ATRI: {
      STATE: {
        LOAD_SUCCESS: "mitt:atri:state:load_success",
        LOAD_FAILED: "mitt:atri:state:load_failed"
      },
      STOP_ACTION: {
        FAILED: "mitt:atri:stop_action:failed",
        SUCCESS: "mitt:atri:stop_action:success",
      }
    },
    SOCKET_CONTEXT: {
      STATE: {
        CHANGE: 'socket_context:state:change'
      },
      CONNECT: {
        SUCCESS: 'mitt:socket_context:connect:success',
        FAILED: 'mitt:socket_context:connect:failed'
      },
      DISCONNECT: {
        FORCE: 'mitt:socket_context:disconnect:force',
        FAILED: 'mitt:socket_context:disconnect:failed',
        SUCCESS: 'mitt:socket_context:disconnect:success'
      }
    },
    ADMIN_FUNCTION: {
      ENABLE: {
        SUCCESS: 'mitt:admin_function:enable:success',
        FAILED: 'mitt:admin_function:enable:failed',
      },
      DISABLE: {
        SUCCESS: 'mitt:admin_function:disable:success',
        FAILED: 'mitt:admin_function:disable:failed'
      },
    }
  },
  // socketio事件
  SOCKETIO: {
    CONNECT: {
      REJECT: "socketio:connect:reject",
      ACCEPT: "socketio:connect:accept",
    },
    DISCONNECT: "socketio:disconnect",
    ATRI: {
      STATE: {
        CHANGE: 'socketio:atri:state:change'
      }
    }
  },
}