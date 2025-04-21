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
      () => store.getters.history.botManagementHistory)

    const onDashboardMenuItemSelected = (name) => {
      navigator.toBotManagement(name)
    }

    const dashboardMenuItems = [
      {
        name: 'overview',
        path: '/workspace/bot-management/overview',
        span: t('view.workspace.BotManagement.overview'),
      },
    ]

    onMounted(() => {
      store.dispatch('setHistory', {
        name: 'workspaceHistory', history: 'bot-management'
      })
      navigator.toBotManagementHistory()
    })

    return {
      activeMenuItem,
      dashboardMenuItems,
      onDashboardMenuItemSelected
    }
  }
}
</script>
<template>
  <CommonNavbar :menu-items="dashboardMenuItems"
                :active-menu-item="activeMenuItem"
                :on-menu-item-selected="onDashboardMenuItemSelected" />
  <RouterView />
</template>
<style scoped>
</style>
