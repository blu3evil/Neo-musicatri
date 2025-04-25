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
      () => store.getters.history.userManagementHistory)

    const userManagementMenuItems = [
      {
        name: 'overview',
        path: '/workspace/user-management/overview',
        span: t('view.workspace.UserManagement.overview'),
      },
      {
        name: 'management',
        path: '/workspace/user-management/management',
        span: t('view.workspace.UserManagement.management'),
      },
    ]

    onMounted(() => {
      store.dispatch('setHistory', {
        name: 'workspaceHistory', history: 'user-management'
      })
      navigator.toUserManagementHistory()
    })

    return {
      navigator,
      activeMenuItem,
      userManagementMenuItems,
    }
  }
}
</script>
<template>
  <CommonNavbar :menu-items="userManagementMenuItems"
                :active-menu-item="activeMenuItem"
                :on-menu-item-selected="navigator.toUserManagement" />
  <RouterView />
</template>
<style scoped>
</style>
