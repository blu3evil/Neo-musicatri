<!-- 用户登录 -->
<script>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import CommonNavbar from '../components/common-navbar.vue'
import PendingPanel from '@/components/pending-panel.vue'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import { createCommonClient } from '@/client/index.js'
import { HttpCode } from '../code.js'


export default {
  name: 'UserLogin',
  components: {
    CommonNavbar /* 导航栏 */,
    PendingPanel /* 等待页面 */,
  },

  setup() {
    const { t } = useI18n() // 本地化
    const store = useStore() // 存储
    const client = createCommonClient() // axios客户端
    const config = store.getters.config

    const retryInterval = 5000 // 重试时间，定义重新轮询间隔

    const currentRetryTimesDisplay = ref(false)  // 当前尝试次数显示
    const retryTimes = ref(0)

    const ellipsis = ref('.') // 等待动画字符串
    const checkingLoginStatusTitleDisplay = ref(false) // 等待校验登录状态
    const revivingAtriTitleDisplay = ref(false) // 尝试修复亚托莉
    const expiredCredentialTitleDisplay = ref(false) // 过期的登录凭证
    const notLoginYetTitleDisplay = ref(false) // 还没有登录过

    const authenticateFailTitleDisplay = ref(false)  // 认证失败
    const authenticateSuccessTitleDisplay = ref(false) // 认证成功

    const checkingAtriStatusTitleDisplay = ref(false) // 正在检查服务端状态
    const connectExceptionTitleDisplay = ref(false)  // 连接异常显示
    const clientExceptionTitleDisplay = ref(false) // 服务端错误显示
    const serverExceptionTitleDisplay = ref(false) // 客户端错误显示
    const unknownExceptionTitleDisplay = ref(false) // 未知异常
    const discordOauth2RedirectLinkDisplay = ref(false)  // discord oauth2重定向链接显示
    const retryLoginLinkDisplay = ref(false)  // 尝试重新登录
    const retryObtainDiscordOauth2LinkDisplay = ref(false)  // 尝试冲i性能获取discord oauth2授权
    const sendingIssueLinkDisplay = ref(false)  // 发送issue链接

    const successMessage = ref(null) // 成功消息
    const exceptionMessage = ref(null) // 错误消息

    let titleStringIntervalId = '' // 动画字符串循环时间id
    let revivingAtriIntervalId = '' // 修复亚托莉轮询事件id
    let atriStatusCheckingIntervalId = '' // 服务端健康状态轮询检查id

    const accessToken = computed(() => store.getters.accessToken)  // 登录校验token

    const clientId = config['DISCORD_CLIENT_ID']
    const redirectUrl = `${config['PUBLIC_URL']}/api/oauth2/discord/callback`
    const scope = config['DISCORD_OAUTH2_SCOPE']  // discord oauth2 token权限范围定义
    const issueLink = config['ISSUE_LINK']  // issue链接

    /*
    * identify: 基础权限，能够通过/users/@me获取用户信息而无需email
    * guilds: 可以通过/users/@me/guilds请求用户所在的所有组信息
    * guilds.join: 这个token可以被用于直接将用户邀请进入某个组/guilds/{guild.id}/members/{user.id}
    */

    // discord oauth2重定向地址
    const discordOauth2RedirectURI = `https://discord.com/api/oauth2/authorize?client_id=${clientId}&redirect_uri=${redirectUrl}&response_type=code&scope=${scope}`

    /**
     * 清除所有显示，用于重置pending-panel显示内容，重新绘制显示信息
     */
    const erasePanel = () => {
      eraseTitle()
      eraseMessage()
      eraseLink()
    }

    // 仅擦除标题
    const eraseTitle = () => {
      // 清除标题显示
      checkingLoginStatusTitleDisplay.value = false
      checkingAtriStatusTitleDisplay.value = false
      revivingAtriTitleDisplay.value = false
      authenticateSuccessTitleDisplay.value = false
      expiredCredentialTitleDisplay.value = false
      notLoginYetTitleDisplay.value = false
      authenticateFailTitleDisplay.value = false
    }

    // 擦除消息
    const eraseMessage = () => {
      // 擦除消息
      successMessage.value = null
      exceptionMessage.value = null
      unknownExceptionTitleDisplay.value = false
      clientExceptionTitleDisplay.value = false
      serverExceptionTitleDisplay.value = false
      discordOauth2RedirectLinkDisplay.value = false
      connectExceptionTitleDisplay.value = false
      currentRetryTimesDisplay.value = false
    }

    // 擦除链接
    const eraseLink = () => {
      retryLoginLinkDisplay.value = false
      retryObtainDiscordOauth2LinkDisplay.value = false
      discordOauth2RedirectLinkDisplay.value = false
      sendingIssueLinkDisplay.value = false
    }

    // 渲染等待字符串动画
    const renderEllipsis = () => {
      ellipsis.value = '.'
    }

    // 亚托莉状态检测循环，通过axios请求后端健康检查接口，返回的状态码表当前状态
    const doCheckAtriStatus = async () => {
      try {
        const response = await client.get('/api/system/health')
        return response.data // 返回响应
      } catch (error) {
        let code = axiosErrorAdaptor(error)
        return { code: code, message: error.message, data: error }
      }
    }

    // 连接错误码，出现这一类错误意味着服务器断联，进入reviveAtri状态轮询检查状态
    const connectErrorCodes = [HttpCode.SERVER_TIMEOUT, HttpCode.AXIOS_NETWORK_ERROR]
    // 客户端错误响应码，出现这一类错误调用onClientException进行回显
    const clientErrorCodes = [HttpCode.CLIENT_ERROR, HttpCode.INVALID_REQUEST_PARAMS]
    // 服务端错误响应码，出现这一类错误调用onServerException进行回显
    const serverErrorCodes = [HttpCode.NETWORK_ERROR, HttpCode.INTERNAL_SERVER_ERROR]

    // 由于token异常引发的问题，需要清空token
    const tokenErrorCodes = [HttpCode.TOKEN_SESSION_INACTIVE,HttpCode.TOKEN_INVALID,HttpCode.TOKEN_EXPIRED]

    // 处理axios客户端异常，将axios响应码适配到项目需要的响应码
    const axiosErrorAdaptor = error => {
      let code
      if (error.code === 'ECONNABORTED') {
        code = HttpCode.SERVER_TIMEOUT // 服务端超时
      } else if (error.code === 'ERR_NETWORK') {
        code = HttpCode.AXIOS_NETWORK_ERROR // 网络错误
      } else if (error.code === 'ERR_BAD_REQUEST')  {
        code = HttpCode.CLIENT_ERROR  // 客户端请求出错
      }
      else {
        code = HttpCode.CLIENT_ERROR // 未知错误
      }
      return code
    }

    // 正在检查亚托莉状态
    const onCheckingAtriStatus = async () => {
      erasePanel()
      renderEllipsis()
      checkingAtriStatusTitleDisplay.value = true // 显示正在检查Atri状态

      let response = await doCheckAtriStatus()  // 执行一次健康检查
      let code = response.code

      if (code === HttpCode.SUCCESS) {
        // 亚托莉状态正常，执行认证逻辑
        return await onAuthenticate()
      } else if (connectErrorCodes.includes(code)) {
        // 连接状态异常，尝试重连，切换到修复亚托莉状态
        renderConnectExceptionMessage(response.message)
        onRevivingAtri()
      }
    }

    // 修复亚托莉
    const onRevivingAtri = () => {
      eraseTitle()
      eraseLink()  // 擦除后保留消息
      renderEllipsis()
      clearInterval(revivingAtriIntervalId)
      retryTimes.value = 1 // 清空重试次数
      revivingAtriTitleDisplay.value = true // 修复亚托莉
      revivingAtriIntervalId = setInterval(async () => {
        const response = await doCheckAtriStatus() // 执行循环获得响应
        let code = response.code
        if (code === HttpCode.SUCCESS) {  // 亚托莉状态恢复
          clearInterval(revivingAtriIntervalId) // 清除循环
          return await onCheckingAtriStatus()
        } else if (connectErrorCodes.includes(code)) {  // 服务端异常
          renderConnectExceptionMessage(response.message)
          retryTimes.value += 1 // 记录重试次数
        }
      }, retryInterval)
    }

    // 亚托莉状态检查守护进程
    const setupAtriStatusCheckingInterval = () => {
      clearInterval(atriStatusCheckingIntervalId)  // 避免循环堆积
      atriStatusCheckingIntervalId = setInterval(async () => {
        let response = await doCheckAtriStatus()
        let code = response.code
        if (connectErrorCodes.includes(code)) {  // 连接出现错误
          clearInterval(atriStatusCheckingIntervalId)  // 中断循环
          renderConnectExceptionMessage(response.message)
          onRevivingAtri()
        }
      }, retryInterval)
    }

    const renderExceptionMessage = (message, titleDisplay) => {
      eraseMessage() // 擦除显示
      titleDisplay.value = true
      exceptionMessage.value = message // 设置错误回显
    }

    // 客户端错误
    const renderClientExceptionMessage = message =>
      renderExceptionMessage(message, clientExceptionTitleDisplay)
    // 服务端异常
    const renderServerExceptionMessage = message =>
      renderExceptionMessage(message, serverExceptionTitleDisplay)
    // 未知异常
    const renderUnknownExceptionMessage = message =>
      renderExceptionMessage(message, unknownExceptionTitleDisplay)
    // 连接异常
    const renderConnectExceptionMessage = message => {
      eraseMessage() // 擦除显示
      currentRetryTimesDisplay.value = true
      connectExceptionTitleDisplay.value = true
      exceptionMessage.value = message // 设置错误回显
    }
      // renderExceptionMessage(message, connectExceptionTitleDisplay)

    // 认证失败
    const onAuthenticateFail = () => {
      eraseTitle()
      authenticateFailTitleDisplay.value = true
      retryObtainDiscordOauth2LinkDisplay.value = true
      retryLoginLinkDisplay.value = true  // 尝试重新登录
      setupAtriStatusCheckingInterval()  // 开启守护进程检查
    }

    // 正在检查登录状态
    const onCheckingLoginStatus = () => {
      erasePanel()
      renderEllipsis()
      clearInterval(atriStatusCheckingIntervalId)
      checkingLoginStatusTitleDisplay.value = true // 正在检查登陆状态
    }

    // 授权工作流
    const onAuthenticate = async () => {
      // 切换到正在检查用户登录状态
      onCheckingLoginStatus()
      // console.log(accessToken.value)
      if ([null, 'null', ''].includes(accessToken.value)) {
        // token不存在，用户还未登录
        onAuthCodeAuthenticate()
      } else {
        // access token存在，使用access token认证
        let response = await doAccessTokenAuthenticate()
        let code = response.code
        let data = response.data
        if (code === HttpCode.SUCCESS) {  // 20000
          erasePanel()
          authenticateSuccessTitleDisplay.value = true  // 认证成功
          // 需要检查是否响应了一个access token，如果存在那么设置进入本地
          if (data['access_token'] != null) {
            // 授权不为空，通常意味着后端帮忙更新了access token
            await store.dispatch('setAccessToken', data['access_token'])
          }

          // todo:执行其他流程

          // 存在两种需要单独判断的情况:
          // - PERMISSION_DENIED: 账号被禁用
          // - TOKEN_SESSION_INACTIVE: 会话被关闭
        } else if (code === HttpCode.PERMISSION_DENIED) {
          // 权限拒绝，通常由于用户还未注册，或是权限被禁用
          eraseTitle()
          renderClientExceptionMessage(response.message)
          authenticateFailTitleDisplay.value = true
          setupAtriStatusCheckingInterval()  // 开启守护进程检查
        } else if (tokenErrorCodes.includes(code)) {
          // 连接已经被关闭，通常由于服务端关闭用户连接
          // token无效，这通常是由于access token，discord access token或discord refresh三者中
          // 某一者失效，或是在刷新refresh token期间发现refresh token过期
          eraseTitle()
          renderClientExceptionMessage(response.message)
          authenticateFailTitleDisplay.value = true
          retryObtainDiscordOauth2LinkDisplay.value = true  // 重新获取授权

          // 清除用户access token，将access token置为null
          store.commit('setAccessToken', null)
          setupAtriStatusCheckingInterval()  // 开启守护进程检查

        } else if (clientErrorCodes.includes(code)) {
          // 认证失败，不执行跳转
          onAuthenticateFail()
          renderClientExceptionMessage(response.message)
        } else if (serverErrorCodes.includes(code)) {
          // 服务端内部错误，例如网络错误等
          eraseTitle()
          authenticateFailTitleDisplay.value = true
          sendingIssueLinkDisplay.value = true  // 显示发送issue链接
          retryObtainDiscordOauth2LinkDisplay.value = true
          retryLoginLinkDisplay.value = true  // 尝试重新登录

          setupAtriStatusCheckingInterval()  // 开启守护进程检查
          renderServerExceptionMessage(response.message)
        } else if (connectErrorCodes.includes(code)) {
          // 连接异常，执行状态检查跳转
          renderConnectExceptionMessage(response.message)
          onRevivingAtri()
        } else {
          // 未知错误，不执行跳转
          console.log(response.code)
          onAuthenticateFail()
          renderUnknownExceptionMessage(response.message)
        }
      }
    }

    // 还未登录
    const onAuthCodeAuthenticate = () => {
      erasePanel()
      setupAtriStatusCheckingInterval() // 启动守护进程
      notLoginYetTitleDisplay.value = true
      discordOauth2RedirectLinkDisplay.value = true
    }

    // access token登入
    const doAccessTokenAuthenticate = async () => {
      try {
        let response = await client.post('/api/auth/validate')
        return response.data
      } catch (error) {
        let code = axiosErrorAdaptor(error)
        return { code: code, message: error.message, data: error }
      }
    }

    // 当页面挂载
    onMounted(() => {
      onCheckingAtriStatus()
      titleStringIntervalId = setInterval(() => {
        ellipsis.value = ellipsis.value.length < 4 ? ellipsis.value + '.' : '.'
      }, 500)
    })

    onUnmounted(() => {
      clearInterval(titleStringIntervalId)
      clearInterval(revivingAtriIntervalId)
      clearInterval(atriStatusCheckingIntervalId)
    })

    return {
      t, // 本地化
      checkingLoginStatusTitleDisplay, // 检查登录状态
      notLoginYetTitleDisplay, // 未登录
      expiredCredentialTitleDisplay, // 凭证过期
      authenticateSuccessTitleDisplay, // 认证成功
      authenticateFailTitleDisplay,  // 认证失败
      checkingAtriStatusTitleDisplay, // 正在检查亚托莉状态
      clientExceptionTitleDisplay, // 客户端异常
      serverExceptionTitleDisplay, // 服务端异常
      connectExceptionTitleDisplay, // 连接异常
      unknownExceptionTitleDisplay, // 未知异常
      revivingAtriTitleDisplay, // 正在修复亚托莉
      currentRetryTimesDisplay, // 当前尝试次数统计显示
      sendingIssueLinkDisplay, // 发送issue链接
      ellipsis,

      retryTimes, // 重试次数
      exceptionMessage, // 错误消息
      successMessage, // 成功消息

      discordOauth2RedirectLinkDisplay,  // discord重定向显示
      discordOauth2RedirectURI,
      issueLink,  // issue链接
      retryLoginLinkDisplay,  // 尝试重新登入链接
      retryObtainDiscordOauth2LinkDisplay,  // 重新获取discord oauth2授权
      onAuthenticate  // 尝试重新授权认证
    }
  },
}
</script>

<template>
  <div class="background" />  <!-- 背景图片 -->
  <CommonNavbar />
  <PendingPanel>
    <!-- 检查登录状态 -->
    <h2 v-if="checkingAtriStatusTitleDisplay">
      <!-- 检查亚托莉状态 -->
      {{ t('view.UserLogin.checking_musicatri_status') }}{{ ellipsis }}
    </h2>
    <h2 v-if="checkingLoginStatusTitleDisplay">
      <!-- 检查当前登录状态 -->
      {{ t('view.UserLogin.checking_login_status') }}{{ ellipsis }}
    </h2>
    <h2 v-if="notLoginYetTitleDisplay">
      <!-- 用户还未登录 -->
      {{ t('view.UserLogin.not_login_yet') }}
    </h2>
    <h2 v-if="expiredCredentialTitleDisplay">
      <!-- 认证过期 -->
      {{ t('view.UserLogin.expired_credential') }}
    </h2>
    <h2 v-if="authenticateSuccessTitleDisplay">
      <!-- 认证成功 -->
      {{ t('view.UserLogin.authenticate_success') }}
    </h2>
    <h2 v-if="authenticateFailTitleDisplay">
      <!-- 认证失败 -->
      {{ t('view.UserLogin.authenticate_fail') }}
    </h2>
    <h2 v-if="revivingAtriTitleDisplay">
      <!-- 恢复亚托莉 -->
      {{ t('view.UserLogin.fixing_musicatri') }}{{ ellipsis }}
    </h2>

    <span v-if="currentRetryTimesDisplay">
      ({{ t('view.UserLogin.current_retry_times', { times: retryTimes }) }})
    </span>

    <h3 class="text-error">
      <span v-if="clientExceptionTitleDisplay">
        <!-- 客户端异常 -->
        ×[{{ t('view.UserLogin.client_exception') }}]</span
      >
      <span v-if="serverExceptionTitleDisplay">
        <!-- 服务端异常 -->
        ×[{{ t('view.UserLogin.server_exception') }}]</span
      >
      <span v-if="unknownExceptionTitleDisplay">
        <!-- 未知异常 -->
        ×[{{ t('view.UserLogin.unknown_exception') }}]
      </span>
      <span v-if="connectExceptionTitleDisplay">
        <!-- 连接异常 -->
        ×[{{ t('view.UserLogin.connect_exception') }}]
      </span>
      <span>{{ exceptionMessage }}</span>
    </h3>
    <h3 class="text-success">{{ successMessage }}</h3>

    <a
      class="option-link"
      v-if="discordOauth2RedirectLinkDisplay"
      :href="discordOauth2RedirectURI"
    >
      >{{ t('view.UserLogin.to_discord') }}
    </a>
    <br v-if="discordOauth2RedirectLinkDisplay && sendingIssueLinkDisplay" />
    <a
      class="option-link"
      v-if="sendingIssueLinkDisplay"
      :href="issueLink"
      target="_blank"
    >
      >{{ t('view.UserLogin.sending_issue') }}</a
    >
    <br v-if="sendingIssueLinkDisplay && retryLoginLinkDisplay" />
    <a
      class="option-link"
      v-if="retryLoginLinkDisplay"
      href="/"
      v-on:click.prevent="onAuthenticate"
    >
      <!-- 尝试重新登入 -->
      >{{ t('view.UserLogin.retry_login') }}
    </a>
    <br v-if="retryObtainDiscordOauth2LinkDisplay && retryLoginLinkDisplay" />
    <!-- 链接换行 -->
    <a
      class="option-link"
      v-if="retryObtainDiscordOauth2LinkDisplay"
      :href="discordOauth2RedirectURI"
    >
      >{{ t('view.UserLogin.retry_auth_code') }}
    </a>
  </PendingPanel>
</template>

<style scoped>
.option-link {
  //margin-left: 6px;
}

.background {
  background-image: url('/src/assets/user-login/ev000al.jpg');
}

</style>
