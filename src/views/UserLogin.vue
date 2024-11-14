<!--suppress ALL -->
<script>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  onUnmounted,
  ref,
  toRef,
  useTemplateRef,
  watch,
} from 'vue'
import CommonNavbar from '@/components/common-navbar.vue'
import CommonPanel from '@/components/common-panel.vue'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import { AbstractState, StateContext } from '@/utils.js'
import { getAuthorizeUrl, userLogin } from '@/services/auth-service.js'
import { createHealthCheck, getSystemHealth } from '@/services/system-service.js'

export default {
  name: 'UserLogin',
  components: {
    CommonNavbar /* 导航栏 */,
    CommonPanel /* 面板 */,
  },
  setup() {
    const store = useStore() // 存储
    const { t } = useI18n() // 本地化
    const panelRef = useTemplateRef('panel-ref') // 面板
    const config = store.getters.config // 配置

    let defaultInterval = 5000 // 默认间隔时间
    let defaultReconnectMaxTimes = 3 // 默认最大允许重连次数
    let context = null // 登录状态上下文

    const healthcheck = createHealthCheck() // 健康检查

    // 检查亚托莉服务状态
    class CheckMusicatriServerState extends AbstractState {
      async enter(context) {
        // console.log('checking atri status')
        panelRef.value.setTitle(
          t('view.UserLogin.checking_musicatri_status'),
          true,
        )
        try {
          if (await getSystemHealth()) {  // 状态健康，进入校验自身登陆情况状态
            context.setState(new CheckUserLoginState())
          } else {
            // 服务异常，无法继续，切换到错误状态
            console.log('musicatri server error')
            context.setState(ErrorState.serverErrorState(response.statusText))
          }
        } catch (error) {
          // axios发生异常
          if (error.code === 'ERR_NETWORK' || error.code === 'ECONNABORTED') {
            // 对于连接超时，本地连接超时，进入轮询等待状态，等待服务器响应正常
            context.setState(new ReconnectMusicatriServerState(error))
          } else {
            context.setState(ErrorState.clientErrorState(error))
          }
        }
      }

      fadeout(context) {
        panelRef.value.clearTitle()
      }
    }

    // 重新连接Musicatri服务状态，通常是服务断开连接需要重新连接
    class ReconnectMusicatriServerState extends AbstractState {
      // 支持传入上一次的异常进行渲染
      constructor(_error) {
        super()
        this.reconnectTimes = 1 // 重试次数
        this.reconnectInterval = defaultInterval // 重连间隔
        this.reconnectMaxTimes = defaultReconnectMaxTimes // 最大重连次数
        this._error = _error
      }

      updateReconnectTimes() {
        panelRef.value.setSubtitle(
          `(${t('view.UserLogin.current_retry_times', { times: this.reconnectTimes })})`,
        )
      }

      async enter(context) {
        panelRef.value.setTitle(t('view.UserLogin.error_occur_title'), true)
        this.updateReconnectTimes()
        panelRef.value.setMessage(this._error, true)

        // todo: 也许可读性更高的错误回显
        // 此处等待亚托莉恢复正常
        await new Promise((resolve, reject) => {
          // 定义健康检查函数，定时查询亚托莉状态检测其是否恢复
          const healthCheck = async () => {
            try {
              if (await getSystemHealth()) {
                resolve() // 完成promise
                context.setState(new CheckMusicatriServerState()) // 切换状态
              } else {
                // todo: 非200，将异常响应到ErrorState，停止重试
                context.setState(
                  ErrorState.serverErrorState(response.statusText),
                )
              }
            } catch (error) {
              // axios发生异常
              if (
                error.code === 'ERR_NETWORK' ||
                error.code === 'ECONNABORTED'
              ) {
                // 仅仅对于这两种异常需要执行重连
                this.reconnectTimes++ // 计数器+1
                if (this.reconnectTimes > this.reconnectMaxTimes) {
                  // 已经超过最大重连次数，停止重试
                  resolve()
                  context.setState(new ReachReconnectLimitState())
                } else {
                  // 还没有超过最大重连次数，继续尝试重连
                  panelRef.value.setMessage(error, true)
                  this.updateReconnectTimes()
                  setTimeout(healthCheck, this.reconnectInterval) // 再次循环
                }
              } else {
                resolve()
                context.setState(ErrorState.clientErrorState(error))
              }
            }
          }
          setTimeout(healthCheck, this.reconnectInterval)
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
        try {
          const response = await userLogin()
          if (response.status === 200) {
            // 认证成功，跳转到用户主页
            console.log('user already login, redirect to home page...')
            // todo: 执行跳转逻辑...
          } else if (response.status === 401) {
            // 用户未登录，切换到等待登录状态
            context.setState(new AwaitingRedirectDiscordOauthState())
          } else if (response.status === 403) {
            // 用户状态被禁用
            context.setState(ErrorState.clientErrorState(response.statusText))
          } else {
            // 响应失败，跳转到ErrorState
            context.setState(ErrorState.serverErrorState(error))
          }
        } catch (error) {
          // 出现axios错误，跳转回到轮询检查atri状态
          if (error.code === 'ERR_NETWORK' || error.code === 'ECONNABORTED') {
            context.setState(new ReconnectMusicatriServerState(error))
          } else {
            // 非正常错误，跳转到ErrorState
            context.setState(ErrorState.clientErrorState(error))
          }
        }
      }

      fadeout(context) {
        panelRef.value.clearTitle()
      }
    }

    // 等待重定向到discord页面
    class AwaitingRedirectDiscordOauthState extends AbstractState {
      constructor() {
        super()
      }

      async enter(context) {
        panelRef.value.setTitle(t('view.UserLogin.not_login_yet'), false)
        const response = await getAuthorizeUrl()
        panelRef.value.addLink({
          desc: t('view.UserLogin.to_discord'),
          href: response.data.authorize_url,
        })

        // 启用健康检查
        healthcheck.begin(() =>
          context.setState(new ReconnectMusicatriServerState(error)),
        )
      }

      fadeout(context) {
        panelRef.value.clearTitle()
        panelRef.value.clearLinks()
        healthcheck.stop() // 停止健康检查
      }
    }

    class ReachReconnectLimitState extends AbstractState {
      enter(context) {
        panelRef.value.setTitle(t('view.UserLogin.reach_reconnect_limit'))
        panelRef.value.setSubtitle(
          `(${t('view.UserLogin.reach_reconnect_limit_subtitle')})`,
        )
        panelRef.value.addLink({
          desc: t('view.UserLogin.try_reconnect'),
          href: '/',
          click: () => {
            panelRef.value.clearTitle()
            panelRef.value.clearLinks()
            context.setState(new ReconnectMusicatriServerState()) // 重置状态到重新连接
          },
        })
        panelRef.value.addIssueLink()
      }
      fadeout(context) {}
    }

    // 错误状态，可用于辅助渲染错误
    class ErrorState extends AbstractState {
      constructor(_title, _message) {
        super()
        this.message = _message
        this.title = _title
      }

      // 客户端异常
      static clientErrorState(message) {
        return new ClientErrorState(message)
      }

      // 服务端异常
      static serverErrorState(message) {
        return new ServerErrorState()
      }

      // 未知异常
      static unknownErrorState(message) {
        return new UnknownErrorState(message)
      }

      enter(context) {
        panelRef.value.setTitle(this.title)
        panelRef.value.setMessage(this.message, true)
        panelRef.value.addLink({
          desc: t('view.UserLogin.retry_login'),
          click: () => {
            context.setState(new CheckMusicatriServerState()) // 从最初开始检查
          },
          href: '/',
        })
        healthcheck.begin(() =>
          context.setState(new ReconnectMusicatriServerState(error)),
        ) // 开启健康检查
      }
      fadeout(context) {
        panelRef.value.clearTitle()
        panelRef.value.clearMessage()
        panelRef.value.clearLinks()
        healthcheck.stop() // 停止健康检查
      }
    }

    class ClientErrorState extends ErrorState {
      constructor(_message) {
        super(t('view.UserLogin.client_error'), _message)
      }
    }

    class ServerErrorState extends ErrorState {
      constructor(_message) {
        super(t('view.UserLogin.server_error'), _message)
      }

      enter(context) {
        super.enter(context)
        panelRef.value.addIssueLink()
      }
    }

    class UnknownErrorState extends ErrorState {
      constructor(_message) {
        super(t('view.UserLogin.unknown_error'), _message)
      }

      enter(context) {
        super.enter(context)
        panelRef.value.addIssueLink()
      }
    }

    onMounted(() => {
      context = new StateContext()
      context.setState(new CheckMusicatriServerState())
    })

    // 在组件销毁之前完成panel执行
    onBeforeUnmount(() => {
      context.setState(null)
    })

    onUnmounted(() => {
      healthcheck.stop() // 清理健康检查
    })
  },
}
</script>
<template>
  <div class="background" />
  <!-- 背景图片 -->
  <CommonNavbar />
  <!-- 导航栏 -->
  <CommonPanel ref="panel-ref" />
  <!-- 面板 -->
</template>

<style scoped>
.background {
  background-image: url('/src/assets/user-login/ev000al.jpg');
}
</style>
