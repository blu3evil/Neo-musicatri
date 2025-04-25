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
      () => store.getters.history.appManagementHistory)

    const onDashboardMenuItemSelected = (name) => {
      navigator.toAppManagement(name)
    }

    const dashboardMenuItems = [
      {
        name: 'overview',
        path: '/workspace/app-management/overview',
        span: t('view.workspace.Dashboard.overview'),
      },
      {
        name: 'logs',
        path: '/workspace/app-management/logs',
        span: t('view.workspace.Dashboard.log_monitoring'),
      }
    ]

    onMounted(() => {
      store.dispatch('setHistory', {
        name: 'workspaceHistory', history: 'app-management'
      })
      navigator.toAppManagementHistory()
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
