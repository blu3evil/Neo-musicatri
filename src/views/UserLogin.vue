<!--suppress JSUnresolvedReference -->
<script>
import CommonNavbar from '@/components/common-navbar.vue'
import CommonPanel from '@/components/common-panel.vue'
import { useI18n } from 'vue-i18n'
import { onBeforeUnmount, onMounted, onUnmounted, useTemplateRef } from 'vue'
import { AbstractState, StateContext } from '@/pattern.js'
// import { useSystemHealthCheck } from '@/services'
import { navigateHelper } from '@/router.js'
import CommonBackground from '@/components/common-background.vue'
import { useStore } from 'vuex'
import { authService } from '@/services/auth-service.js'
import { systemService } from '@/services/system-service.js'
import { initUserSocket } from '@/sockets/socket-client.js'

export default {
  name: 'UserLogin',
  components: {
    CommonBackground /* 背景 */,
    CommonNavbar /* 导航栏 */,
    CommonPanel /* 面板 */,
  },
  setup() {
    const { t } = useI18n() // 本地化
    const panelRef = useTemplateRef('panel-ref') // 面板
    const bgRef = useTemplateRef('bg-ref')
    const store = useStore()
    const config = store.getters.config

    const systemHealthcheckInterval = config['SYSTEM_HEALTH_CHECK_INTERVAL']
    let maxReconnectTimes = config['MAX_RECONNECT_TIMES'] // 默认最大允许重连次数
    let context = null // 登录状态上下文

    // const healthcheck = useSystemHealthCheck() // 健康检查

    // 检查亚托莉服务状态
    class CheckMusicatriServerState extends AbstractState {
      async enter(context) {
        // console.log('checking atri status')
        panelRef.value.setTitle(
          t('view.UserLogin.checking_musicatri_status'),
          true,
        )
        const result = await systemService.getSystemHealth()
        if (result.isSuccess()) {
          // 状态健康，进入校验自身登陆情况状态
          context.setState(new CheckUserLoginState())
        } else {
          // 将异常归类为client server unknown 3类进行分类处理
          ErrorState.handleErrorResult(result)
        }
      }

      fadeout(context) {
        panelRef.value.clearTitle()
      }
    }

    // 重新连接Musicatri服务状态，通常是服务断开连接需要重新连接
    class ReconnectMusicatriServerState extends AbstractState {
      // 支持传入上一次的异常进行渲染
      constructor(message) {
        super()
        this.reconnectTimes = 1 // 重试次数
        this.message = message
      }

      updateReconnectTimes() {
        panelRef.value.setSubtitle(
          `(${t('view.UserLogin.current_retry_times', { times: this.reconnectTimes })})`,
        )
      }

      async enter(context) {
        panelRef.value.setTitle(t('view.UserLogin.connection_error'), true)
        this.updateReconnectTimes()
        panelRef.value.setMessage(this.message, true)

        // todo: 也许可读性更高的错误回显
        // 此处等待亚托莉恢复正常
        await new Promise((resolve, reject) => {
          // 定义健康检查函数，定时查询亚托莉状态检测其是否恢复
          const healthCheck = async () => {
            const result = await systemService.getSystemHealth()
            if (result.isSuccess()) {
              resolve() // 完成promise
              context.setState(new CheckMusicatriServerState()) // 切换状态
            } else if (result.isConnectionError()) {
              // 仅仅对于这两种异常需要执行重连
              this.reconnectTimes++ // 计数器+1
              if (this.reconnectTimes > maxReconnectTimes) {
                // 已经超过最大重连次数，停止重试
                reject()
                context.setState(new ReachReconnectLimitState())
              } else {
                // 还没有超过最大重连次数，继续尝试重连
                panelRef.value.setMessage(result.message, true)
                this.updateReconnectTimes()
                setTimeout(healthCheck, systemHealthcheckInterval) // 再次循环
              }
            } else {
              // 对于一般错误分类后处理
              reject()
              ErrorState.handleErrorResult(result)
            }
          }
          setTimeout(healthCheck, systemHealthcheckInterval)
        })
      }

      fadeout(context) {
        panelRef.value.clearTitle()
        panelRef.value.clearMessage()
      }
    }

    // 检查用户自身登录状态
    class CheckUserLoginState extends AbstractState {
      async enter(context) {
        // console.log('checking login status')
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

    // 建立socketio连接
    class BuildSocketConnectionState extends AbstractState {
      async enter(context) {
        panelRef.value.setTitle(
          t('view.UserLogin.build_socket_connection'),
          true,
        )

        const result = await initUserSocket()  // 初始化socketio连接
        console.log(result)

        if (result.isSuccess()) {
          // 连接建立成功，将用户引导到主页
          await navigateHelper.toUserHome()
        } else {
          // 其他返回码使用分类处理器
          ErrorState.handleErrorResult(result)
        }
      }

      fadeout(context) {
        panelRef.value.clearTitle()
      }
    }

    // 等待重定向到discord页面
    class AwaitingRedirectDiscordOauthState extends AbstractState {
      async enter(context) {
        panelRef.value.setTitle(t('view.UserLogin.not_login_yet'), false)
        this.addAuthorizeLink()
        // 开启健康检查
        // healthcheck.begin(result =>
        //   context.setState(new ReconnectMusicatriServerState(result.message)),
        // )
      }

      addAuthorizeLink() {
        panelRef.value.addLink({
          desc: t('view.UserLogin.to_discord'),
          href: '/',
          click: () => context.setState(new TryingAuthorizeState()),
        })
      }

      fadeout(context) {
        panelRef.value.clearTitle()
        panelRef.value.clearLinks()
        // healthcheck.stop() // 停止健康检查
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

    class ReachReconnectLimitState extends AbstractState {
      enter(context) {
        panelRef.value.setTitle(t('view.UserLogin.reach_reconnect_limit'))
        panelRef.value.setSubtitle(
          `(${t('view.UserLogin.reach_reconnect_limit_subtitle')})`,
        )
        this.addRetryConnectLink()
        panelRef.value.addIssueLink()
      }
      fadeout(context) {}

      addRetryConnectLink() {
        panelRef.value.addLink({
          desc: t('view.UserLogin.try_reconnect'),
          href: '/',
          click: () => {
            panelRef.value.clearTitle()
            panelRef.value.clearLinks()
            context.setState(new ReconnectMusicatriServerState()) // 重置状态到重新连接
          },
        })
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
        if (errorResult.isClientError()) {
          context.setState(ErrorState.clientErrorState(message))
        } else if (errorResult.isServerError()) {
          context.setState(ErrorState.serverErrorState(message))
        } else if (errorResult.isConnectionError()) {  // 连接错误
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

      static connectionErrorState(message) {
        return new ConnectionErrorState(message)
      }

      enter(context) {
        panelRef.value.setTitle(this.title)
        panelRef.value.setMessage(this.message, true)
        // healthcheck.begin(result =>
        //   context.setState(new ReconnectMusicatriServerState(result.message)),
        // ) // 开启健康检查
      }

      // 添加issue链接
      addIssueLink() {
        panelRef.value.addIssueLink()
      }

      // 添加重新登录连接
      addReturnLink() {
        panelRef.value.addLink({
          desc: t('view.UserLogin.retry_login'),
          click: () => context.setState(new CheckMusicatriServerState()), // 从最初开始检查,
          href: '/',
        })
      }

      fadeout(context) {
        panelRef.value.clearTitle()
        panelRef.value.clearMessage()
        panelRef.value.clearLinks()
        // healthcheck.stop() // 停止健康检查
      }
    }

    class ClientErrorState extends ErrorState {
      constructor(message) {
        super(t('view.UserLogin.client_error'), message)
      }

      enter(context) {
        super.enter(context)
        super.addReturnLink()
      }
    }

    // 连接错误状态
    class ConnectionErrorState extends ErrorState {
      constructor(message) {
        super(t('view.UserLogin.error_occur_title'), message)
      }

      enter(context) {
        super.enter(context)
        this.addRetryConnectLink()
      }

      // 重试连接
      addRetryConnectLink() {
        panelRef.value.addLink({
          desc: t('view.UserLogin.retry_connect'),
          click: () => context.setState(new CheckMusicatriServerState()), // 从最初开始检查,
          href: '/',
        })
      }
    }

    class ServerErrorState extends ErrorState {
      constructor(_message) {
        super(t('view.UserLogin.server_error'), _message)
      }

      enter(context) {
        super.enter(context)
        super.addReturnLink()
        super.addIssueLink()
      }
    }

    class UnknownErrorState extends ErrorState {
      constructor(message) {
        super(t('view.UserLogin.unknown_error'), message)
      }

      enter(context) {
        super.enter(context)
        super.addReturnLink()
        super.addIssueLink()
      }
    }

    onMounted(async () => {
      // 阻塞加载背景图片
      await bgRef.value.loadAsync('/src/assets/user-login/ev000al.jpg')
      context = new StateContext()
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
  <CommonNavbar />
  <CommonPanel ref="panel-ref" />
</template>
