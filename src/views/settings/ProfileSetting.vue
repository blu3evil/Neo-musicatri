<script>
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { onMounted } from 'vue'

export default {
  setup() {
    const store = useStore()  // 存储
    const { t } = useI18n()

    onMounted(() => {
      store.dispatch('setHistory', {
        name: 'settingsHistory', history: 'profile'
      })
    })

    return {
      t,  // 本地化
    }
  }
}
</script>

<template>
  <h1 class="unselectable">{{t("view.ProfileSetting.title")}}</h1>
</template>

<style scoped>

</style>
