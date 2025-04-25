<script>
import CommonNavbar from '@/components/common-navbar.vue'
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { navigator } from '@/router.js'

export default {
  components: {
    CommonNavbar
  },
  setup() {
    const { t } = useI18n()
    const store = useStore()
    const activeMenuItem = computed(
      () => store.getters.history.musiclibManagementHistory)

    const musiclibManagementMenuItems = [
      {
        name: 'overview',
        path: '/workspace/musiclib-management/overview',
        span: t('view.workspace.MusiclibManagement.overview'),
      },
      {
        name: 'management',
        path: '/workspace/musiclib-management/management',
        span: t('view.workspace.MusiclibManagement.management'),
      },
    ]

    onMounted(() => {
      store.dispatch('setHistory', {
        name: 'workspaceHistory', history: 'musiclib-management'
      })
      navigator.toMusiclibManagementHistory()
    })

    return {
      navigator,
      activeMenuItem,
      musiclibManagementMenuItems,
    }
  }
}
</script>
<template>
  <CommonNavbar :menu-items="musiclibManagementMenuItems"
                :active-menu-item="activeMenuItem"
                :on-menu-item-selected="navigator.toMusicLibManagement" />
  <RouterView />
</template>
<style scoped>
</style>
