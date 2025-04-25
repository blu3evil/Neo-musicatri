<!--suppress JSUnresolvedReference -->
<script>
import SystemInformation from '@/components/system-information.vue'
import EllipsisString from '@/components/ellipsis-string.vue'
import AdminFunctionPanel from '@/components/admin-function-panel.vue'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { atriAudio } from '@/utils/media-helper.js'
import { computed, onMounted } from 'vue'
import { authServiceV1 } from '@/services/auth-service.js'
import { config } from '@/config.js'

export default {
  components: {
    EllipsisString,
    SystemInformation,
    AdminFunctionPanel,  /* 管理员功能管理 */
  },
  setup() {
    const { t } = useI18n()
    const store = useStore()
    const activeTheme = computed(() => store.getters.activeTheme) // 当前主题
    const isAdmin = computed(() => authServiceV1.checkRole('admin'))

    const onDiscordIconClick = () =>
      window.open(config['DISCORD_LINK'], '_blank')
    const onGithubIconClick = () =>
      window.open(config['GITHUB_LINK'], '_blank')

    onMounted(() => {
      store.dispatch('setHistory', {
        name: 'settingsHistory', history: 'about'
      })
    })

    return {
      t,
      activeTheme,
      isAdmin,
      onGithubIconClick,
      onDiscordIconClick,
      authService: authServiceV1,
      atriAudio,
    }
  },
}
</script>

<template>
  <el-row>
    <el-col :span="24">
      <h1 class="unselectable">{{ t('view.AboutSetting.title') }}</h1>
    </el-col>
  </el-row>
  <div class="setting-divider" />
  <div class="about-setting">
    <el-row>
      <el-col :span="24">
        <h4 class="unselectable">
          {{ t('view.AboutSetting.musicatri_audio1') }}
          <span @click="atriAudio.playHighPerformances()">🔊</span>
        </h4>
        <h4 class="unselectable">
          {{ t('view.AboutSetting.musicatri_audio2') }}
        </h4>
        <h4 class="unselectable">
          {{ t('view.AboutSetting.musicatri_audio3') }}
        </h4>
      </el-col>
    </el-row>
    <div class="setting-divider" />

    <SystemInformation />  <!-- 服务端信息 -->
    <AdminFunctionPanel v-if="isAdmin" />  <!-- 管理员功能 -->

    <!-- discord链接 -->
    <el-row style="margin-top: 60px">
      <span class="unselectable">
        <el-popover
          placement="top-start"
          trigger="hover"
          popper-class="navbar-popper"
          popper-style="width: 230px"
          :content="t('view.AboutSetting.discord_logo')"
        >
          <template #reference>
            <div class="unselectable">
              <img
                src="/src/assets/common-navbar/icon-discord.png"
                style="height: 36px; margin: 3px"
                @click="onDiscordIconClick"
                alt="discord logo"
              />
            </div>
          </template>
        </el-popover>
      </span>

      <!-- github链接 -->
      <span class="unselectable">
        <el-popover
          placement="top-start"
          trigger="hover"
          popper-class="navbar-popper"
          :content="t('view.AboutSetting.github_logo')"
        >
          <template #reference>
            <img
              :src="
                activeTheme === 'dark'
                  ? '/src/assets/common-navbar/icon-github.png'
                  : '/src/assets/about-setting/github-mark.png'
              "
              style="height: 39px; margin-left: 20px"
              @click="onGithubIconClick"
              alt="github logo"
            />
          </template>
        </el-popover>
      </span>
    </el-row>
  </div>
</template>

<style scoped>
</style>
