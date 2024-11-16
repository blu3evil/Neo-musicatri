<!-- discord认证页面 -->
<!--suppress JSUnresolvedReference -->
<script>
import CommonNavbar from '@/components/common-navbar.vue'
import CommonPanel from '@/components/common-panel.vue'
import { useI18n } from 'vue-i18n'
import { onBeforeUnmount, onMounted, ref, useTemplateRef } from 'vue'
import { AbstractState, StateContext } from '@/utils.js'
import { getAuthorizeUrl, userAuthorize } from '@/services/auth-service.js'
import { useRouter } from 'vue-router'

export default {
  components: {
    CommonPanel,
    CommonNavbar,
  },

  setup() {
    const { t } = useI18n() // 本地化
    const router = useRouter() // 路由
    let context = null

    const panelRef = useTemplateRef('panel-ref') // 面板引用
    const imageUrl = ref('/src/assets/user-login-callback/ev005al.png')

    // 预加载图片
    const preloadImage = _imageUrl => {
      const img = new Image()
      img.src = _imageUrl // 使用错误响应时的背景
      img.onload = () => (imageUrl.value = img.src) // 等待图片加载完成后再刷新
    }

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
          const result = await userAuthorize(code) // 执行用户登入
          if (result.isSuccess()) {
            // 认证成功，切换到认证成功状态
            context.setState(new AuthSuccessState())
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

    // 授权成功，倒计时3s后响应到主页
    class AuthSuccessState extends AbstractState {
      constructor() {
        super()
        this.surplus = 3 // 倒计时
        this.countdownIntervalId = 0 // 倒计时循环id
      }

      // 更新链接
      updateLink() {
        panelRef.value.clearLinks()
        panelRef.value.addLink({
          desc: `${t('view.UserLoginCallback.return_login')}(${this.surplus})`,
          click: () => router.push('/'),
        })
      }

      async enter(context) {
        preloadImage('/src/assets/user-login-callback/ev005cl.png')
        panelRef.value.setTitle(t('view.UserLoginCallback.auth_success'))
        this.updateLink()
        this.countdownIntervalId = setInterval(() => {
          // 倒计时回退
          this.surplus--
          if (this.surplus <= 0) {
            clearInterval(this.countdownIntervalId)
            router.push('/')
          }
          this.updateLink()
        }, 1000)
      }

      fadeout(context) {
        panelRef.value.clearTitle()
        panelRef.value.clearLinks()
        clearInterval(this.countdownIntervalId)
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
          click: () => router.push('/'),
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
        preloadImage('/src/assets/user-login-callback/ev005bl.png')
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
        const result = await getAuthorizeUrl()
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

    onMounted(() => {
      context = new StateContext() // 状态上下文
      context.setState(new AwaitingAuthResponseState())
    })

    onBeforeUnmount(() => {
      context.setState(null)
    })

    return {
      imageUrl,
    }
  },
}
</script>

<template>
  <div class="background" :style="{ backgroundImage: `url(${imageUrl})` }" />
  <CommonNavbar />
  <CommonPanel ref="panel-ref" />
</template>

<style scoped></style>
