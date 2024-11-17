<!--suppress JSValidateTypes -->
<script>
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { computed, onMounted, ref, watch } from 'vue'
import { availableThemes } from '@/theme/index.js' // 可用主题
import {
  availableLanguages,
  getLanguageDisplayName,
  getActiveLanguage,
  localstorageTag,
} from '@/locale/index.js'

export default {
  // 计算属性

  setup() {
    const { t, locale } = useI18n() // 本地化
    const activeLanguage = ref('')
    const store = useStore() // 存储

    const activeTheme = computed({
      get() { return store.getters.activeTheme },
      set(value) {
        store.dispatch('setActiveTheme', value)
      },
    })

    /**
     * 监听activeLanguage变化，并且在变化之后更新语言
     */
    watch(activeLanguage, (newVal, oldVal) => {
      if (newVal !== oldVal) {
        if (availableLanguages.indexOf(newVal) !== -1) {
          localStorage.setItem(localstorageTag, newVal) // 在localstorage设置语言
          activeLanguage.value = newVal // 当前语言
          locale.value = newVal // 切换语言，更新响应式
        }
      }
    })

    /**
     * 加载当前激活语言
     */
    const loadActiveLanguage = () => {
      activeLanguage.value = getActiveLanguage()
    }

    onMounted(() => {
      loadActiveLanguage()
    })

    return {
      t, // 本地化
      activeLanguage,
      availableLanguages, // 可用语言列表
      getLanguageDisplayName,
      availableThemes, // 可用主题
      activeTheme, // 当前激活主题
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
        <span class="unselectable text-small">{{
          t('view.AppearanceSetting.language_setting_description')
        }}</span>
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
              v-for="lang in availableLanguages"
              :key="lang"
              :label="getLanguageDisplayName(lang)"
              :value="lang"
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
