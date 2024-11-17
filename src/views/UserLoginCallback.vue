<!-- discord认证页面 -->
<!--suppress JSUnresolvedReference -->
<script>
import CommonNavbar from '@/components/common-navbar.vue'
import CommonPanel from '@/components/common-panel.vue'
import { useI18n } from 'vue-i18n'
import { onBeforeUnmount, onMounted, useTemplateRef } from 'vue'
import { AbstractState, StateContext } from '@/utils.js'
import { useAuthService } from '@/services/auth-service.js'
import { useNavigateHelper } from '@/router.js'
import CommonBackground from '@/components/common-background.vue'

export default {
  components: {
    CommonBackground,
    CommonPanel,
    CommonNavbar,
  },

  setup() {
    const { t } = useI18n() // 本地化
    const navigateHelper = useNavigateHelper()
    let context = null

    const bgRef = useTemplateRef('bg-ref')
    const panelRef = useTemplateRef('panel-ref') // 面板引用
    const authService = useAuthService()

    // 初始状态，等待授权响应
    class AwaitingAuthResponseState extends AbstractState {
      async enter(context) {
        // 解析url获取discord授权码
        const query = new URLSearchParams(window.location.search)
        const code = query.get('code')

        if (code) {
          // 授权码存在，执行认证流程
          panelRef.value.setTitle(
            t('component.pending-panel.waiting_response'),
            true,
          )
          const result = await authService.authorize(code) // 执行用户登入
          if (result.isSuccess()) {
            // 认证成功，切换到认证成功状态
            // await bgRef.value.loadAsync('/src/assets/user-login-callback/ev005cl.png')
            context.setState(new UserLoginStatus())
          } else {
            // 分4类处理异常
            ErrorState.handleErrorResult(result)
          }
        } else {
          // 授权码不存在
          let message = t('view.UserLoginPending.invalid_auth_code')
          context.setState(ErrorState.clientErrorState(message))
        }
      }

      fadeout(context) {
        panelRef.value.clearTitle()
      }
    }

    // 执行用户登入逻辑
    class UserLoginStatus extends AbstractState {
      async enter(context) {
        // console.log('checking login status')
        panelRef.value.setTitle(t('view.UserLoginCallback.user_login'), true)
        const result = await authService.login()
        if (result.isSuccess()) {
          // 认证成功，尝试建立socketio连接后跳转到用户主页
          context.setState(new BuildSocketConnectionState())
        } else {
          ErrorState.handleErrorResult(result)
        }
      }

      fadeout(context) {
        panelRef.value.clearTitle()
      }
    }

    // 建立socketio连接
    class BuildSocketConnectionState extends AbstractState {
      async enter(context) {
        panelRef.value.setTitle(
          t('view.UserLogin.build_socket_connection'), true)
        // 尝试建立socketio连接
        const result = await authService.verifyLoginStatus()
        if (result.isSuccess()) {
          // 连接建立成功，将用户引导到主页
          await navigateHelper.toUserIndex()
        } else {
          // 其他返回码使用分类处理器
          ErrorState.handleErrorResult(result)
        }
      }

      fadeout(context) {
        panelRef.value.clearTitle()
      }
    }

    // 错误状态，可用于辅助渲染错误
    class ErrorState extends AbstractState {
      constructor(_title, _message) {
        super()
        this.message = _message
        this.title = _title
      }

      static handleErrorResult(errorResult) {
        const message = errorResult.message
        if (errorResult.isClientError()) {
          context.setState(ErrorState.clientErrorState(message))
        } else if (errorResult.isServerError()) {
          context.setState(ErrorState.serverErrorState(message))
        } else if (errorResult.isConnectionError) {
          context.setState(ErrorState.connectionErrorState(message))
        } else {
          context.setState(ErrorState.unknownErrorState(message))
        }
      }

      // 客户端异常
      static clientErrorState(message) {
        return new ClientErrorState(message)
      }

      // 服务端异常
      static serverErrorState(message) {
        return new ServerErrorState(message)
      }

      // 未知异常
      static unknownErrorState(message) {
        return new UnknownErrorState(message)
      }

      // 连接状态异常
      static connectionErrorState(message) {
        return new ConnectionErrorState(message)
      }

      // 增加重新登录链接
      addReturnLink() {
        panelRef.value.addLink({
          desc: t('view.UserLoginCallback.return_login'),
          click: () => navigateHelper.toUserLogin(),
          href: '/',
        })
      }

      // 增加重新授权链接
      async addRetryLink() {
        panelRef.value.addLink({
          desc: t('view.UserLoginCallback.retry_authorize'),
          href: '/',
          click: () => context.setState(new TryingAuthorizeState()),
        })
      }

      enter(context) {
        bgRef.value.loadAsync('/src/assets/user-login-callback/ev005bl.png')
        panelRef.value.setTitle(this.title)
        panelRef.value.setMessage(this.message, true)
      }

      fadeout(context) {
        panelRef.value.clearTitle()
        panelRef.value.clearMessage()
        panelRef.value.clearLinks()
      }
    }

    class ClientErrorState extends ErrorState {
      constructor(message) {
        super(t('view.UserLogin.client_error'), message)
      }

      enter(context) {
        super.enter(context)
        super.addReturnLink()
        super.addRetryLink()
      }

      fadeout(context) {
        super.fadeout(context)
      }
    }

    // 尝试重新授权状态，从后端重新拉取授权链接并在成功之后执行跳转
    class TryingAuthorizeState extends AbstractState {
      async enter(context) {
        panelRef.value.setTitle(
          t('view.UserLoginCallback.awaiting_authorize'),
          true,
        )
        const result = await authService.getAuthorizeUrl()
        if (result.isSuccess()) {
          // 成功拉取授权链接，切换到等待用户登录状态
          window.location.href = result.data.authorize_url // 跳转到授权链接
        } else {
          // 分类处理一般异常错误
          ErrorState.handleErrorResult(result)
        }
      }

      fadeout(context) {
        panelRef.value.clearTitle() // 擦除标题
      }
    }

    // 服务器连接失败状态
    class ConnectionErrorState extends ErrorState {
      constructor(message) {
        super(t('view.UserLogin.connection_error'), message)
      }

      enter(context) {
        super.enter(context)
        super.addReturnLink()
        super.addRetryLink()
      }

      fadeout(context) {
        super.fadeout(context)
      }
    }

    class ServerErrorState extends ErrorState {
      constructor(_message) {
        super(t('view.UserLogin.server_error'), _message)
      }
      enter(context) {
        super.enter(context)
        super.addReturnLink()
        panelRef.value.addIssueLink()
        super.addRetryLink()
      }

      fadeout(context) {
        super.fadeout(context)
      }
    }

    class UnknownErrorState extends ErrorState {
      constructor(_message) {
        super(t('view.UserLogin.unknown_error'), _message)
      }

      enter(context) {
        super.enter(context)
        panelRef.value.addIssueLink()
        super.addReturnLink()
      }

      fadeout(context) {
        super.fadeout(context)
      }
    }

    onMounted(async () => {
      // 加载背景图片
      await bgRef.value.loadAsync('/src/assets/user-login-callback/ev005al.png')
      context = new StateContext() // 状态上下文
      context.setState(new AwaitingAuthResponseState())
    })

    onBeforeUnmount(() => {
      context.setState(null)
    })
  },
}
</script>

<template>
  <CommonBackground ref="bg-ref" />
  <CommonNavbar />
  <CommonPanel ref="panel-ref" />
</template>
