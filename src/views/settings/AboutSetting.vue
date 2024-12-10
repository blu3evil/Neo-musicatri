<!--suppress JSUnresolvedReference -->
<script>
import EllipsisString from '@/components/ellipsis-string.vue'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { onMounted, ref } from 'vue'
import { audioPlayer } from '@/utils/media-helper.js'
import { computed } from 'vue'
import { systemService } from '@/services/system-service.js'
import { authService } from '@/services/auth-service.js'
import { adminSocketContext } from '@/sockets/admin-socket.js'
import { ToastMessage } from '@/utils/ui-helper.js'
import { config } from '@/config.js'

export default {
  components: {
    EllipsisString,
  },
  setup() {
    const store = useStore() // 存储
    const { t } = useI18n()
    const popperStyle = ref() // 弹出框统一样式
    const loadingSystemInfo = ref(true)

    const onGithubIconClick = () => window.open(config['GITHUB_LINK'], '_blank')
    const activeTheme = computed(() => store.getters.activeTheme) // 当前主题
    const adminSocketStatus = computed(() => store.getters.adminSocketStatus)

    const dashboardConnectStatusStr = computed(() => {
      switch (adminSocketStatus.value) {
        case 'connected': return t('view.AboutSetting.connected')
        case 'connecting': return t('view.AboutSetting.connecting')
        case 'unconnected': return t('view.AboutSetting.unconnected')
      }
    })

    // 建立到admin socketio的连接
    const onConnectDashboardClick = async () => {
      const status = adminSocketStatus.value
      if (status === 'unconnected') {
        // 建立连接
        const result = await adminSocketContext.connect()
        if (result.isSuccess()) {
          // 连接成功
          audioPlayer.play('/src/assets/about-setting/dashboard-welcome.wav')
          ToastMessage.success(t('sockets.admin-socket.connect_success'))
        } else {
          // 连接失败
          ToastMessage.error(result.message)
        }
      } else if (status === 'connected') {
        // 断开连接
        const result = await adminSocketContext.disconnect()
        if (result.isSuccess()) {
          // 断开连接成功
          ToastMessage.success(t('sockets.admin-socket.disconnect_success'))
        } else {
          // 断开连接失败
          ToastMessage.error(result.message)
        }
      }
    }

    const onDiscordIconClick = () =>
      window.open(config['DISCORD_LINK'], '_blank')

    const highPerformanceWAVs = [
      '/src/assets/about-setting/high-performance-1.WAV',
      '/src/assets/about-setting/high-performance-2.WAV',
      '/src/assets/about-setting/high-performance-3.WAV',
      '/src/assets/about-setting/high-performance-4.WAV',
      '/src/assets/about-setting/high-performance-5.WAV',
      '/src/assets/about-setting/high-performance-6.WAV',
      '/src/assets/about-setting/high-performance-7.WAV',
      '/src/assets/about-setting/high-performance-8.WAV',
      '/src/assets/about-setting/high-performance-9.WAV',
    ]

    const systemInfo = ref({
      name: '...',
      version: '...',
      description: '...',
    })

    const initSystemInfo = async () => {
      const result = await systemService.getSystemInfo()
      if (result.isSuccess()) {
        // 成功获取服务信息
        systemInfo.value = result.data
      } else {
        // todo: 添加重试获取服务器信息逻辑
      }
    }

    onMounted(() => {
      store.dispatch('setActiveSettingMenuItem', 'about')
      initSystemInfo()
    })

    return {
      t, // 本地化
      config,
      popperStyle,
      activeTheme, // 当前主题
      systemInfo,
      loadingSystemInfo,
      highPerformanceWAVs,
      dashboardConnectStatusStr,
      adminSocketStatus,
      onGithubIconClick,
      onDiscordIconClick,
      onConnectDashboardClick,
      authService,
      audioPlayer,
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
          <span @click="audioPlayer.playRandomly(highPerformanceWAVs)">🔊</span>
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
    <!-- 服务端信息 -->
    <el-row style="margin-top: 40px">
      <el-col :span="24">
        <h2 class="unselectable">{{ t('view.AboutSetting.system_info') }}</h2>
      </el-col>
    </el-row>
    <el-row>
      <span class="text-small unselectable">
        {{ t('view.AboutSetting.system_name') }}: {{ systemInfo['name'] }}
      </span>
    </el-row>
    <el-row>
      <span class="text-small unselectable">
        {{ t('view.AboutSetting.system_version') }}: {{ systemInfo['version'] }}
      </span>
    </el-row>
    <el-row>
      <span class="text-small unselectable">
        {{ t('view.AboutSetting.system_description') }}:
        {{ systemInfo['description'] }}
      </span>
    </el-row>

    <el-row v-if="authService.verifyRole('admin')" style="margin-top: 40px">
      <!-- 连接到仪表盘 -->
      <el-col :span="5">
        <span class="text-small unselectable">
          {{ t('view.AboutSetting.dashboard_connection') }}:
        </span>
        <span class="text-small unselectable">
          <EllipsisString
            :message="dashboardConnectStatusStr"
            :ellipsis="adminSocketStatus === 'connecting'"
          />
        </span>
      </el-col>
      <el-col :span="19">
        <el-button
          type="primary"
          class="text-small"
          style="height: 30px; width: 180px"
          @click="onConnectDashboardClick"
          :loading="adminSocketStatus === 'connecting'"
        >
          <span v-if="adminSocketStatus !== 'connected'">
            {{ t('view.AboutSetting.connect_dashboard') }}
          </span>
          <span v-else>
            {{ t('view.AboutSetting.disconnect_dashboard') }}
          </span>
        </el-button>
      </el-col>
    </el-row>

    <!-- discord链接 -->
    <el-row style="margin-top: 60px">
      <span class="unselectable">
        <el-popover
          placement="top-start"
          :width="320"
          trigger="hover"
          popper-class="navbar-popper"
          :content="t('component.common-navbar.discord_logo')"
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
          :width="310"
          trigger="hover"
          popper-class="navbar-popper"
          :content="t('component.common-navbar.github_logo')"
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
