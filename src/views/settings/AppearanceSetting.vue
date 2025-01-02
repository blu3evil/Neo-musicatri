<!--suppress JSValidateTypes -->
<script>
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { computed, onMounted } from 'vue'
import { availableThemes } from '@/theme/index.js'
import { availableLanguages } from '@/locale/index.js'

export default {
  setup() {
    const { t, locale } = useI18n() // 本地化
    const store = useStore() // 存储

    const activeTheme = computed({  // 监听主题变化
      get() { return store.getters.activeTheme },
      set(value) { store.dispatch('setActiveTheme', value) }
    })

    // 语言修改需要在vue组件中进行
    const activeLanguage = computed({  // 监听语言变化
      get() { return store.getters.activeLanguage },
      set(value) {
        store.dispatch('setActiveLanguage', value).then(() =>
          locale.value = store.getters.activeLanguage)
      }
    })

    onMounted(() => {
      store.dispatch('setHistory', {
        name: 'settingsHistory', history: 'appearance'
      })
    })

    return {
      t, // 本地化
      activeTheme, // 当前激活主题
      availableThemes, // 可用主题
      activeLanguage,  // 当前激活语言
      availableLanguages,  // 可用语言
    }
  },
}
</script>

<template>
  <el-row>
    <el-col :span="24">
      <h1 class="unselectable">{{ t('view.AppearanceSetting.title') }}</h1>
    </el-col>
  </el-row>
  <!-- 语言设定 -->
  <div class="setting-divider" />
  <div class="appearance-setting">
    <el-row>
      <el-col :span="24">
        <h2 class="unselectable">
          {{ t('view.AppearanceSetting.language_setting') }}
        </h2>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="14">
        <span class="unselectable text-small" style="color: var(--text-color-2)">
          {{ t('view.AppearanceSetting.language_setting_description') }}</span>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="15" style="margin-top: 15px">
        <span class="unselectable text-small">
          {{ t('view.AppearanceSetting.language_select_label') }}
          <el-select
            v-model="activeLanguage"
            :placeholder="
              t('view.AppearanceSetting.language_select_placeholder')
            "
            size="default"
            placement="bottom"
            style="width: 240px"
          >
            <el-option
              v-for="(lang, key) in availableLanguages"
              :key="lang"
              :label="lang['name']"
              :value="key"
            />
          </el-select>
        </span>
      </el-col>
    </el-row>
  </div>

  <!-- 主题设定 -->
  <div class="setting-divider" />
  <div class="appearance-setting">
    <el-row>
      <el-col :span="24">
        <h2 class="unselectable">
          {{ t('view.AppearanceSetting.theme_setting') }}
        </h2>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="15" style="margin-top: 15px">
        <span class="unselectable text-small">
          {{ t('view.AppearanceSetting.theme_select_label') }}
          <el-select
            v-model="activeTheme"
            :placeholder="t('view.AppearanceSetting.theme_select_placeholder')"
            size="default"
            placement="bottom"
            style="width: 240px"
          >
            <el-option
              v-for="(theme, key) in availableThemes"
              :key="theme"
              :label="theme['name']"
              :value="key"
            />
          </el-select>
        </span>
      </el-col>
    </el-row>
  </div>
</template>
<style scoped></style>
