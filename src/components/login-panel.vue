<!-- 重定向小卡片 -->
<script>
import { computed, getCurrentInstance } from 'vue'
import { useI18n } from 'vue-i18n'

export default {
  setup() {
    const instance = getCurrentInstance()
    const config = instance.appContext.config.globalProperties.$config
    // discord application client id
    const clientId = config['DISCORD_CLIENT_ID']
    // discord oauth2回调地址，改前端
    const redirectUrl = `${config['PUBLIC_URL']}/api/oauth2/discord/callback`
    // discord oauth2 token权限范围定义
    const scope = "identify guilds guilds.join"

    /*
    * identify: 基础权限，能够通过/users/@me获取用户信息而无需email
    * guilds: 可以通过/users/@me/guilds请求用户所在的所有组信息
    * guilds.join: 这个token可以被用于直接将用户邀请进入某个组/guilds/{guild.id}/members/{user.id}
    */

    // discord oauth2重定向地址
    const redirectUri = `https://discord.com/api/oauth2/authorize?client_id=${clientId}&redirect_uri=${redirectUrl}&response_type=code&scope=${scope}`
    const redirectUriDesc = computed(() => `> ${t('component.redirect-panel.to_discord')}`)

    // console.log(redirectUri)
    // console.log(redirectUrl)
    const { t } = useI18n()  // 本地化
    return {
      t,  // 本地化
      redirectUri,
      redirectUriDesc
    }
  }
}

</script>
<template>
  <el-row class="row-bg full-height" align="middle" justify="center">
    <el-col :span="9">
      <el-card id="redirect-panel" class="unselectable">  <!-- 设置背景色 -->
        <template #header>
          <div class="card-header">
            <h2>{{t('component.redirect-panel.title')}}</h2>
            <a id="discord-oauth2-redirect-link" :href="redirectUri">{{redirectUriDesc}}</a>
          </div>
        </template>
        <template #footer>{{t('component.redirect-panel.footer')}}</template>
      </el-card>
    </el-col>
  </el-row>
</template>

<style scoped>
#discord-oauth2-redirect-link {
  margin-left: 8px;
}

/* 高度置中 */
.full-height {
  height: 85vh;
}

#redirect-panel {
  background-color: var(--redirect-card-bg-color);  /* 背景色 */
  --el-card-border-color: none;
  box-shadow: var(--box-shadow);  /* 阴影效果 */
  backdrop-filter:blur(12px);  /* 添加模糊效果 */
  border: 1px;
  border-radius: 13px;
  color: var(--text-color);  /* 使用主题字色 */
  overflow: hidden;
  transition: var(--el-transition-duration)
}
</style>
