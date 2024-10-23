<!-- discord认证页面 -->
<script>
import { createCommonClient } from '@/client'
import { computed, getCurrentInstance, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import CommonNavbar from '../components/common-navbar.vue'
import PendingPanel from '../components/pending-panel.vue'
import { getActiveLanguage } from '@/locale/index.js'
import { useStore } from 'vuex'
import { HttpCode } from '@/code.js'
import router from '@/router/index.js'

export default {
  components: { PendingPanel, CommonNavbar: CommonNavbar },
  setup() {
    const successMessage = ref(null) // 成功消息
    const errorMessage = ref(null) // 错误消息

    const { t } = useI18n()  // 本地化
    const store = useStore()  // 存储

    const ellipsis = ref('.')  // 等待动画字符串
    const backgroundImageUrl = ref('/src/assets/user-login-pending/ev005al.png') // 默认背景图片
    let ellipsisAppendIntervalId  // 定时事件id
    let returnLoginPageIntervalId   // 返回主页定时时间id

    const waitingResponseTitleDisplay = ref(true)
    const clientErrorTitleDisplay = ref(false) // 服务端错误显示
    const serverErrorTitleDisplay = ref(false) // 客户端错误显示
    const unknownErrorTitleDisplay = ref(false) // 未知错误
    const loginPageLinkDisplay = ref(false) // 返回登录页链接显示
    const issuePageLinkDisplay = ref(false)  // 发送issue链接

    const authenticateSuccessTitleDisplay = ref(false)  // 授权成功
    const authenticateFailedTitleDisplay = ref(false)  // 授权成功

    const returnLoginPageLinkDisplay = ref(false)  // 返回前端链接
    const returnTimeout = ref(null)  // 返回倒计时

    const config = getCurrentInstance().appContext.config.globalProperties.$config
    const feedbackLink = ref(config['ISSUE_LINK'])

    /**
     * 预加载背景图片，仅仅在图片完成加载后才切换，能够有效避免图片频闪现象出现
     * @param imageUrl 图片相对路径
     */
    const preloadBackgroundImage = imageUrl => {
      const img = new Image()
      img.src = imageUrl // 使用错误响应时的背景
      img.onload = () => (backgroundImageUrl.value = img.src) // 等待图片加载完成后再刷新
    }

    /**
     * 清除所有显示，用于重置pending-panel显示内容，重新绘制显示信息
     */
    const eraseDisplay = () => {
      eraseTitle()
      eraseMessage()
    }

    // 擦除标题
    const eraseTitle = () => {
      ellipsis.value = '.'
      waitingResponseTitleDisplay.value = false
      loginPageLinkDisplay.value = false
      issuePageLinkDisplay.value = false
      authenticateSuccessTitleDisplay.value = false
      authenticateFailedTitleDisplay.value = false
    }

    // 清除消息显示
    const eraseMessage = () => {
      successMessage.value = null
      errorMessage.value = null
      clientErrorTitleDisplay.value = false
      serverErrorTitleDisplay.value = false
      unknownErrorTitleDisplay.value = false
    }

    /**
     * 等待后端响应
     */
    const onWaitingResponse = () => {
      eraseDisplay() // 擦除显示
      waitingResponseTitleDisplay.value = true // 正在等待消息
    }

    /**
     * 客户端错误
     */
    const onClientError = message => {
      eraseDisplay()  // 擦除显示
      authenticateFailedTitleDisplay.value = true
      clientErrorTitleDisplay.value = true
      errorMessage.value = message // 设置错误回显
      loginPageLinkDisplay.value = true // 显示返回链接
      preloadBackgroundImage('/src/assets/user-login-pending/ev005bl.png')
    }

    /**
     * 服务端错误
     */
    const onServerError = message => {
      eraseDisplay()
      authenticateFailedTitleDisplay.value = true
      serverErrorTitleDisplay.value = true
      errorMessage.value = message // 设置错误回显
      loginPageLinkDisplay.value = true // 显示返回链接
      issuePageLinkDisplay.value = true // 显示提交错误日志信息
      preloadBackgroundImage('/src/assets/user-login-pending/ev005bl.png')
    }

    /**
     * 未知错误
     */
    const onUnknownError = message => {
      eraseDisplay() // 擦除显示
      authenticateFailedTitleDisplay.value = true
      unknownErrorTitleDisplay.value = true
      errorMessage.value = message // 设置错误回显
      loginPageLinkDisplay.value = true // 显示返回链接
      issuePageLinkDisplay.value = true // 显示提交错误日志信息
      preloadBackgroundImage('/src/assets/user-login-pending/ev005bl.png')
    }

    /**
     * 将响应结果设置为成功样式
     */
    const onSuccessResponse = (message = null) => {
      eraseDisplay()  // 擦除显示
      authenticateSuccessTitleDisplay.value = true
      successMessage.value = message // 设置消息

      preloadBackgroundImage('/src/assets/user-login-pending/ev005cl.png')
      returnTimeout.value = 3  // 设置倒计时
      returnLoginPageLinkDisplay.value = true  // 显示返回链接
      returnLoginPageIntervalId = setInterval(() => {  // 倒计时回退
        returnTimeout.value -= 1
        if (returnTimeout.value <= 0) {
          router.push('/user/login')
          clearInterval(returnLoginPageIntervalId)
        }
      }, 1000)
    }

    /**
     * 页面主方法，向后端的/api/auth/login接口发送登录凭据请求认证凭据信息，发送discord授权
     * 码，尝试获取认证信息
     */
    const tryAuthenticateWithAuthCode = async () => {
      const query = new URLSearchParams(window.location.search) // 组件创建完成后向后端发送请求获取token
      const code = query.get('code') // 解析url获取discord授权码

      if (code) {
        // 若授权码存在
        let client = createCommonClient() // 创建axios客户端
        const config =
          getCurrentInstance().appContext.config.globalProperties.$config
        try {
          console.log('Accept-Language : ' + getActiveLanguage())
          await client.post("/api/auth/login", { code: code }).then(response => {
              // 处理请求响应
              let code = response.data.code         // 响应码
              let message = response.data.message   // 响应消息
              let data = response.data.data         // 响应数据
              console.log(code, message, data)      // 打印结果

              if (code === HttpCode.SUCCESS) {
                // 认证成功，处理相关认证参数
                store.dispatch('setAccessToken', data.access_token)  // 存储access token
                onSuccessResponse(message)
              } else if (code === HttpCode.INVALID_REQUEST_PARAMS) {
                onServerError(message)  // 服务器内部错误
              } else {
                onClientError(message)  // 客户端错误
              }
            })
        } catch (error) {
          if (error.code === 'ECONNABORTED') {
            // 服务端超时
            console.log(error)
            onServerError(error.message)
          } else if (error.code === 'ERR_NETWORK') {
            // 网络错误
            console.log(error)
            onClientError(error)
          } else {
            // 未知错误
            console.log(error.message)
            onUnknownError(error.message)
          }
        }
      } else {
        // 没有携带授权code参数，客户端错误
        onClientError(t('view.UserLoginPending.invalid_auth_code'))
      }
    }

    onMounted(() => {
      ellipsisAppendIntervalId = setInterval(() => {
        ellipsis.value = ellipsis.value.length < 4 ? ellipsis.value + '.' : '.' // 控制点的数量
      }, 500) // 每 500 毫秒更新一次
      onWaitingResponse()
      tryAuthenticateWithAuthCode() // 发送请求并等待响应
    })

    onUnmounted(() => {
      // 清除定时事件
      clearInterval(ellipsisAppendIntervalId)
      clearInterval(returnLoginPageIntervalId)
    })

    return {
      t, // 本地化
      router,  // 路由
      successMessage,
      errorMessage, // 消息
      backgroundImageUrl,

      // 消息显示
      clientErrorTitleDisplay,  // 客户端错误
      serverErrorTitleDisplay,  // 服务端错误
      waitingResponseTitleDisplay,  // 正在等待响应
      loginPageLinkDisplay,  // 登录页面链接
      issuePageLinkDisplay,  // issue页面链接
      unknownErrorTitleDisplay,  // 未知错误链接
      authenticateSuccessTitleDisplay, // 授权成功
      authenticateFailedTitleDisplay,  // 授权失败

      returnTimeout,  // 返回倒计时
      returnLoginPageLinkDisplay,  // 返回链接

      // 提交issue
      feedbackLink,
      ellipsis
    }
  },
}
</script>

<template>
  <div
    class="background"
    :style="{ backgroundImage: `url(${backgroundImageUrl})` }"
  />
  <!-- 背景图片 -->
  <CommonNavbar />
  <PendingPanel>
    <h2 v-if="waitingResponseTitleDisplay">
      {{ t('component.pending-panel.waiting_response')}}{{ ellipsis }}
    </h2>
    <h2 v-if="authenticateSuccessTitleDisplay">  <!-- 授权成功 -->
      {{ t('component.pending-panel.authenticate_success') }}
    </h2>
    <h2 v-if="authenticateFailedTitleDisplay">  <!-- 授权失败 -->
      {{ t('component.pending-panel.authenticate_failed') }}
    </h2>
    <h3 class="text-success">
      {{ successMessage }}
    </h3>
    <h3 class="text-error">
      <span v-if="serverErrorTitleDisplay">  <!-- 服务端异常 -->
        ×[{{ t('component.pending-panel.server_error') }}]{{ errorMessage }}
      </span>
      <span v-if="clientErrorTitleDisplay">  <!-- 客户端异常 -->
        ×[{{ t('component.pending-panel.client_error') }}]{{ errorMessage }}
      </span>
      <span v-if="unknownErrorTitleDisplay">  <!-- 未知异常 -->
        ×[{{ t('component.pending-panel.unknown_error') }}]{{ errorMessage }}
      </span>
    </h3>

    <a class="option-link" v-if="loginPageLinkDisplay" href="/">
      >{{ t('component.pending-panel.login_page_link') }}
    </a>
    <br v-if="issuePageLinkDisplay" />  <!-- 仅在issuePageLinkDisplay显示时进行换行 -->
    <a class="option-link" v-if="issuePageLinkDisplay" :href="feedbackLink" target="_blank">
      >{{ t('component.pending-panel.issue_page_link') }}
    </a>
    <a class="option-link" v-if="returnLoginPageLinkDisplay" href="/"
       @click.prevent="router.push('/user/login')">>{{ t('component.pending-panel.login_page_link') }} ({{ returnTimeout }}s)
    </a>

  </PendingPanel>
</template>

<style scoped>
/* 引导链接 */
.option-link {
  //margin-left: 6px;
}
/* 成功消息 */
</style>
