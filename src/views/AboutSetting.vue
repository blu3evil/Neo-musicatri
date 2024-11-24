<!--suppress JSUnresolvedReference -->
<script>
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { onMounted, ref } from 'vue'
import { computed } from 'vue'
import { systemService } from '@/services/system-service.js'

export default {
  setup() {
    const store = useStore() // 存储
    const { t } = useI18n()
    const config = store.getters.config
    const popperStyle = ref() // 弹出框统一样式
    const loadingSystemInfo = ref(true)

    const onGithubIconClick = () => window.open(config['GITHUB_LINK'], '_blank')
    const activeTheme = computed(() => store.getters.activeTheme)

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
      '/src/assets/about-setting/high-performance-9.WAV'
    ]

    let audio = null
    const playAudio = url => {
      if (audio !== null) {  // 停止当前
        audio.pause()
        audio.currentTime = 0
      }

      audio = new Audio(url)
      audio.play()  // 播放音频
    }

    const playAudioRandomly = urls => {
      const url = getRandomElement(urls)
      playAudio(url)
    }

    function getRandomElement(arr) {
      if (!Array.isArray(arr) || arr.length === 0) return null
      const randomIndex = Math.floor(Math.random() * arr.length);
      return arr[randomIndex];
    }

    const systemInfo = ref({
      'name': '...',
      'version': '...',
      'description': '...'
    })

    const initSystemInfo = async () => {
      const result = await systemService.getSystemInfo()
      if (result.isSuccess()) {
        // 成功获取服务信息
        systemInfo.value = result.data
      } else {
      }
    }

    onMounted(() => {
      initSystemInfo()
    })

    return {
      t, // 本地化
      config,
      popperStyle,
      activeTheme,  // 当前主题
      onGithubIconClick,
      onDiscordIconClick,
      systemInfo,
      loadingSystemInfo,
      playAudio,
      highPerformanceWAVs,
      playAudioRandomly
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
          <span @click="playAudioRandomly(highPerformanceWAVs)">🔊</span>
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
        {{ t('view.AboutSetting.system_description') }}: {{ systemInfo['description'] }}
      </span>
    </el-row>

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
              :src="activeTheme === 'dark'?
              '/src/assets/common-navbar/icon-github.png':
              '/src/assets/about-setting/github-mark.png'"
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
