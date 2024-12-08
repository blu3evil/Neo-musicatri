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
    const activeDashboardPage = computed(
      () => store.getters.activeDashboardMenuItem)

    const onDashboardMenuItemSelected = (name) => {
      store.dispatch('setActiveDashboardMenuItem', name)
      navigator.toDashboardHistory()
    }

    const dashboardMenuItems = [
      {
        name: 'overview',
        path: '/workspace/dashboard/overview',
        span: t('view.workspace.Dashboard.overview'),
      },
      {
        name: 'users',
        path: '/workspace/dashboard/users',
        span: t('view.workspace.Dashboard.user_management'),
      },
      {
        name: 'logs',
        path: '/workspace/dashboard/logs',
        span: t('view.workspace.Dashboard.log_monitoring'),
      }
    ]

    onMounted(async () => {
      await navigator.toDashboardHistory()
    })

    return {
      activeDashboardPage,
      dashboardMenuItems,
      onDashboardMenuItemSelected
    }
  }
}
</script>
<template>
  <CommonNavbar :menu-items="dashboardMenuItems"
                :active-menu-item="activeDashboardPage"
                :on-menu-item-selected="onDashboardMenuItemSelected" />
  <RouterView />
</template>
<style scoped>
</style>
