<!-- discord认证页面 -->
<!--suppress ALL -->
<script>
import { useClient } from '@/client.js'
import {
  computed,
  getCurrentInstance,
  onBeforeUnmount,
  onMounted,
  onUnmounted,
  ref,
  useTemplateRef,
} from 'vue'
import { useI18n } from 'vue-i18n'
import CommonNavbar from '@/components/common-navbar.vue'
import CommonPanel from '@/components/common-panel.vue'
import { getActiveLanguage } from '@/locale/index.js'
import { AbstractState, StateContext, createHealthCheck } from '@/utils.js'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import router from '@/router.js'

export default {
  components: {
    CommonPanel,
    CommonNavbar,
  },
  setup() {
    const { t } = useI18n() // 本地化
    const store = useStore() // 存储
    const router = useRouter() // 路由
    const client = useClient() // axios客户端
    const config = store.getters.config // 项目配置
    let context = null

    const panelRef = useTemplateRef('panel-ref') // 面板引用
    const imageUrl = ref('/src/assets/user-login-pending/ev005al.png')

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
        const redirectUri = config['DISCORD_OAUTH_REDIRECT_URI']  // 重定向链接

        if (code) {
          // 授权码存在，执行认证流程
          panelRef.value.setTitle(
            t('component.pending-panel.waiting_response'),
            true,
          )

          try {
            const response = await client.post('/auth/authorize',
              { 'code': code, 'redirect_uri': redirectUri })
            if (response.status === 200) {
              // 认证成功，切换到认证成功状态
              context.setState(new AuthSuccessState())
            } else if (response.status === 500) {
              // 服务端错误
              context.setState(ErrorState.serverErrorState(response.statusText))
            } else {
              // 认证失败
              context.setState(ErrorState.clientErrorState(response.statusText))
            }
          } catch (error) {
            // 发生异常
            context.setState(ErrorState.clientErrorState(error))
          }
        } else {
          // 授权码不存在
          context.setState(
            ErrorState.clientErrorState(
              t('view.UserLoginPending.invalid_auth_code'),
            ),
          )
        }
      }

      fadeout(context) {
        panelRef.value.clearTitle()
      }
    }

    // 授权成功，倒计时3s后响应到主页
    class AuthSuccessState extends AbstractState {
      constructor(context) {
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
        preloadImage('/src/assets/user-login-pending/ev005cl.png')
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
        return new UnkonwnErrorState(message)
      }

      enter(context) {
        preloadImage('/src/assets/user-login-pending/ev005bl.png')
        panelRef.value.setTitle(this.title)
        panelRef.value.setMessage(this.message, true)
        panelRef.value.addLink({
          desc: t('view.UserLoginCallback.return_login'),
          click: () => router.push('/'),
          href: '/',
        })
      }
      fadeout(context) {
        panelRef.value.clearTitle()
        panelRef.value.clearMessage()
        panelRef.value.clearLinks()
      }
    }

    class ClientErrorState extends ErrorState {
      constructor(_message) {
        super(t('view.UserLogin.client_error'), _message)
      }
      enter(context) {
        super.enter(context)
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
        panelRef.value.addIssueLink()
      }
      fadeout(context) {
        super.fadeout(context)
      }
    }

    class UnkonwnErrorState extends ErrorState {
      constructor(_message) {
        super(t('view.UserLogin.unknown_error'), _message)
      }
      enter(context) {
        super.enter(context)
        panelRef.value.addIssueLink()
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

    onUnmounted(() => {
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
