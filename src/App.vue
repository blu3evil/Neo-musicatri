<script>
import { ElConfigProvider } from 'element-plus'
import { availableLanguages } from '@/locale/index.js'
import { computed } from 'vue'
import { store } from '@/storage/index.js'

export default {
  setup() {
    const locale = computed(() => availableLanguages[store.getters.activeLanguage].locale)
    return {
      locale
    }
  }
}

</script>

<template>
  <el-config-provider :locale=locale>
    <RouterView />
  </el-config-provider>
</template>

<style scoped>
</style>
