<!-- discord认证页面 -->
<!--suppress JSUnresolvedReference -->
<script>
import MusicatriNavbar from '@/components/musicatri-navbar.vue'
import ActionPanel from '@/components/action-panel.vue'
import CommonBackground from '@/components/common-background.vue'
import { useI18n } from 'vue-i18n'
import { onBeforeUnmount, onMounted, useTemplateRef } from 'vue'
import { AbstractState, StateContext } from '@/pattern.js'
import { authServiceV1 } from '@/services/auth-service.js'
import { navigator } from '@/router.js'
import { config } from '@/config.js'
import { useStore } from 'vuex'

export default {
  components: {
    CommonBackground,
    ActionPanel ,
    MusicatriNavbar,
  },

  setup() {
    const { t } = useI18n() // 本地化
    const store = useStore()
    let context = null

    const bgRef = useTemplateRef('bg-ref')
    const panelRef = useTemplateRef('panel-ref')  // 面板引用

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
          const result = await authServiceV1.userAuthorize(code) // 执行用户认证
          if (result.isSuccess()) {  // 认证成功
            context.setState(new UserLoginStatus())
          } else {  // 分4类处理异常
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
        panelRef.value.setTitle(t('view.UserLoginCallback.user_login'), true)
        const result = await authServiceV1.userLogin()
        if (result.isSuccess()) {
          // 登陆成功后建立socketio连接
          context.setState(new loadCurrentUserDetailsState())
        } else {
          ErrorState.handleErrorResult(result)
        }
      }

      fadeout(context) {
        panelRef.value.clearTitle()
      }
    }

    // 加载当前用户信息
    class loadCurrentUserDetailsState extends AbstractState {
      async enter(context) {
        await bgRef.value.loadAsync('/src/assets/user-login-callback/ev005cl.png')
        panelRef.value.setTitle(
          t('view.UserLogin.load_user_details'), true)

        // 尝试建立socketio连接
        const result = await store.dispatch('loadCurrentUserDetails')

        if (result.isSuccess()) {
          // 连接建立成功，将用户引导到主页
          await navigator.toWorkspaceHistory()
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
      constructor(title, message) {
        super()
        this.message = message
        this.title = title
      }

      static handleErrorResult(errorResult) {
        const message = errorResult.message
        if (errorResult.isClientError()) {  // 客户端异常
          context.setState(new ClientErrorState(message))
        } else if (errorResult.isServerError()) {  // 服务端异常
          context.setState(new ServerErrorState(message))
        } else if (errorResult.isConnectionError) {  // 连接异常
          context.setState(new ConnectionErrorState(message))
        } else {  // 未知异常
          context.setState(new UnknownErrorState(message))
        }
      }

      // 增加重新登录链接
      appendReturnToLoginLink() {
        panelRef.value.appendEventLink(
          t('view.UserLoginCallback.return_login'),
          async () => await navigator.toLogin()
        )
      }

      // 增加重新授权链接
      appendRetryAuthorizeLink() {
        panelRef.value.appendEventLink(
          t('view.UserLoginCallback.retry_authorize'),
          () => context.setState(new TryingAuthorizeState())
        )
      }

      appendSendIssueLink() {
        panelRef.value.appendHrefLink(
          t('view.UserLogin.sending_issue'),
          config['ISSUE_LINK']
        )
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
        super.appendReturnToLoginLink()
        super.appendRetryAuthorizeLink()
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
        const result = await authServiceV1.getAuthorizeUrl()
        if (result.isSuccess()) {
          // 成功拉取授权链接，执行跳转
          window.location.href = result.data.authorize_url
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
        this.addRetryConnectLink()  // 添加重试连接
      }

      fadeout(context) {
        super.fadeout(context)
      }

      // 重试连接
      addRetryConnectLink() {
        panelRef.value.appendEventLink(
          t('view.UserLogin.retry_connect'),
          () => context.setState(new loadCurrentUserDetailsState())
          )
      }
    }

    class ServerErrorState extends ErrorState {
      constructor(message) {
        super(t('view.UserLogin.server_error'), message)
      }
      enter(context) {
        super.enter(context)
        super.appendReturnToLoginLink()
        super.appendRetryAuthorizeLink()
        super.appendSendIssueLink()
      }

      fadeout(context) {
        super.fadeout(context)
      }
    }

    class UnknownErrorState extends ErrorState {
      constructor(message) {
        super(t('view.UserLogin.unknown_error'), message)
      }

      enter(context) {
        super.enter(context)
        super.appendReturnToLoginLink()
        super.appendSendIssueLink()
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
  <MusicatriNavbar />
  <el-row class="row-bg full-height" align="middle" justify="center">
    <el-col :style="{ display: 'flex', alignItems: 'center', justifyContent: 'center' }">
      <ActionPanel ref="panel-ref" />
    </el-col>
  </el-row>
</template>
<style scoped>
/* 高度置中 */
.full-height {
  height: 85vh;
}
</style>
