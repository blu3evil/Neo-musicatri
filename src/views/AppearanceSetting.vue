<!--suppress JSValidateTypes -->
<script>
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { computed, onMounted, ref, watch } from 'vue'
import {
  availableLanguages,
  getLanguageDisplayName,
  getActiveLanguage,
  localstorageTag
} from '@/locale/index.js'

export default {
  setup() {
    const store = useStore()  // 存储
    const {t ,locale} = useI18n()  // 本地化

    const activeLanguage = ref('')
    const selectLangPlaceHolder = computed(() => t('view.AppearanceSetting.language_select_placeholder'))

    /**
     * 监听activeLanguage变化，并且在变化之后更新语言
     */
    watch(activeLanguage, (newVal, oldVal) => {
      if (newVal !== oldVal) {
        if (availableLanguages.indexOf(newVal) !== -1) {
          localStorage.setItem(localstorageTag, newVal);  // 在localstorage设置语言
          activeLanguage.value = newVal  // 当前语言
          locale.value = newVal; // 切换语言，更新响应式
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
      t,  // 本地化
      activeLanguage,
      selectLangPlaceHolder,  // 选择语言占位
      availableLanguages,  // 可用语言列表
      getLanguageDisplayName,
    }
  }
}
</script>

<template>
  <el-row>
    <el-col :span="24">
      <h1 class="unselectable">{{t("view.AppearanceSetting.title")}}</h1>
    </el-col>
  </el-row>
  <el-row>
    <el-col :span="24">
      <h2 class="unselectable">{{t("view.AppearanceSetting.language_setting")}}</h2>
    </el-col>
  </el-row>
  <el-row>
    <el-col :span="14">
      <span class="unselectable text-small">{{t("view.AppearanceSetting.language_setting_description")}}</span>
    </el-col>
  </el-row>
  <el-row>
    <el-col :span="15" style="margin-top: 15px">
      <span class="unselectable text-small">
        {{t('view.AppearanceSetting.language_select_label')}}
      <el-select
        v-model="activeLanguage"
        :placeholder="selectLangPlaceHolder"
        size="default"
        placement="bottom"
        style="width: 240px">
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

</template>

<style scoped>
</style>
