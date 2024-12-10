<!--suppress JSUnresolvedReference -->
<script>
import MusicatriNavbar from '@/components/musicatri-navbar.vue'
import CommonPanel from '@/components/common-panel.vue'
import CommonBackground from '@/components/common-background.vue'
import { useI18n } from 'vue-i18n'
import { onBeforeUnmount, onMounted, onUnmounted, useTemplateRef } from 'vue'
import { AbstractState, StateContext } from '@/pattern.js'
import { navigator } from '@/router.js'
import { authService } from '@/services/auth-service.js'
import { systemService } from '@/services/system-service.js'
import { userSocketContext } from '@/sockets/user-socket.js'
import { config } from '@/config.js'

// todo: 优化登录逻辑，编写管理员登入，完成登出功能编写
export default {
  name: 'UserLogin',
  components: {
    CommonBackground /* 背景 */,
    MusicatriNavbar /* 导航栏 */,
    CommonPanel /* 面板 */,
  },
  setup() {
    const { t } = useI18n() // 本地化
    const panelRef = useTemplateRef('panel-ref') // 面板
    const bgRef = useTemplateRef('bg-ref')
    let context = new StateContext() // 登录状态上下文

    // 1.检查亚托莉服务状态
    class CheckMusicatriServerState extends AbstractState {
      async enter(context) {
        panelRef.value.setTitle(
          t('view.UserLogin.checking_musicatri_status'),
          true,
        )
        // 检查服务端健康状态
        const result = await systemService.getSystemHealth()
        if (result.isSuccess()) {
          // 状态健康，进入校验自身登陆情况状态
          context.setState(new CheckUserLoginState())
        } else {
          // 将异常归类为client server unknown connection_error 4类进行分类处理
          ErrorState.handleErrorResult(result)
        }
      }

      fadeout(context) {
        panelRef.value.clearTitle()
      }
    }

    // 2.检查用户自身登录状态
    class CheckUserLoginState extends AbstractState {
      async enter(context) {
        panelRef.value.setTitle(t('view.UserLogin.checking_login_status'), true)
        const result = await authService.userLogin()
        if (result.isSuccess()) {
          // 认证成功，尝试建立socketio连接后跳转到用户主页
          context.setState(new BuildSocketConnectionState())
        } else if (result.code === 401) {
          // 单独处理401错误，此状态码表示用户没有登入，从后端拉取授权链接
          context.setState(new AwaitingRedirectDiscordOauthState())
        } else {
          ErrorState.handleErrorResult(result)
        }
      }
      fadeout(context) {
        panelRef.value.clearTitle()
      }
    }

    // 3.建立socketio连接
    class BuildSocketConnectionState extends AbstractState {
      async enter(context) {
        panelRef.value.setTitle(
          t('view.UserLogin.build_socket_connection'),
          true,
        )
        const result = await userSocketContext.connect()
        if (result.isSuccess()) {
          await navigator.toWorkspace()  // 连接建立成功，引导用户到工作空间
        } else {
          ErrorState.handleErrorResult(result)  // 处理异常
        }
      }

      fadeout(context) {
        panelRef.value.clearTitle()
      }
    }

    // 4.等待重定向到discord页面
    class AwaitingRedirectDiscordOauthState extends AbstractState {
      async enter(context) {
        panelRef.value.setTitle(t('view.UserLogin.not_login_yet'), false)
        this.addAuthorizeLink()
      }

      addAuthorizeLink() {
        panelRef.value.appendEventLink(
          t('view.UserLogin.to_discord'),
          () => context.setState(new AwaitRedirectDiscordState()))
      }

      fadeout(context) {
        panelRef.value.clearTitle()
        panelRef.value.clearLinks()
      }
    }

    // 尝试重新授权状态，从后端重新拉取授权链接并在成功之后执行跳转
    class AwaitRedirectDiscordState extends AbstractState {
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

    // 错误状态，可用于辅助渲染错误
    class ErrorState extends AbstractState {
      constructor(title, message) {
        super()
        this.message = message
        this.title = title
      }

      // 将异常进行分类处理
      static handleErrorResult(errorResult) {
        const message = errorResult.message
        if (errorResult.isClientError()) {  // 客户端异常
          context.setState(new ClientErrorState(message))
        } else if (errorResult.isServerError()) {  // 服务端异常
          context.setState(new ServerErrorState(message))
        } else if (errorResult.isConnectionError()) {  // 连接异常
          context.setState(new ConnectionErrorState(message))
        } else {  // 未知异常
          context.setState(new UnknownErrorState(message))
        }
      }

      enter(context) {
        panelRef.value.setTitle(this.title)
        panelRef.value.setMessage(this.message, true)
      }

      // 添加issue链接
      appendSendIssueLink() {
        panelRef.value.appendHrefLink(
          t('view.UserLogin.sending_issue'),
          config['ISSUE_LINK']
        )
      }

      // 添加重新登录连接
      appendRetryLoginLink() {
        panelRef.value.appendEventLink(
          t('view.UserLogin.retry_login'),
          () => context.setState(new CheckMusicatriServerState())
        )
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
        super.appendRetryLoginLink()
      }
    }

    // 连接错误状态
    class ConnectionErrorState extends ErrorState {
      constructor(message) {
        super(t('view.UserLogin.error_occur_title'), message)
      }

      enter(context) {
        super.enter(context)
        this.appendRetryConnectLink()
      }

      // 重试连接
      appendRetryConnectLink() {
        panelRef.value.appendEventLink(
          t('view.UserLogin.retry_connect'),
          () => context.setState(new CheckMusicatriServerState())
        )
      }
    }

    class ServerErrorState extends ErrorState {
      constructor(_message) {
        super(t('view.UserLogin.server_error'), _message)
      }

      enter(context) {
        super.enter(context)
        super.appendRetryLoginLink()
        super.appendSendIssueLink()
      }
    }

    class UnknownErrorState extends ErrorState {
      constructor(message) {
        super(t('view.UserLogin.unknown_error'), message)
      }

      enter(context) {
        super.enter(context)
        super.appendRetryLoginLink()
        super.appendSendIssueLink()
      }
    }

    onMounted(async () => {
      // 阻塞加载背景图片
      await bgRef.value.loadAsync('/src/assets/user-login/ev000al.jpg')
      context.setState(new CheckMusicatriServerState())
    })

    // 在组件销毁之前完成panel执行
    onBeforeUnmount(() => {
      context.setState(null)
    })

    onUnmounted(() => {
      // healthcheck.stop() // 清理健康检查
    })
  },
}
</script>
<template>
  <CommonBackground ref="bg-ref" />
  <MusicatriNavbar />
  <CommonPanel ref="panel-ref" />
</template>
