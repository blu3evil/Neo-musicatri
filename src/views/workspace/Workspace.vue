<!-- 项目设置页面 -->
<script>
import MusicatriNavbar from '@/components/musicatri-navbar.vue'
import CommonBackground from '@/components/common-background.vue'
import CommonSidebar from '@/components/common-sidebar.vue'
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { Stopwatch, Compass, User, Files } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { navigator } from '@/router.js'
import { authService } from '@/services/auth-service.js'

export default {
  components: {
    MusicatriNavbar /* 导航栏 */,
    CommonSidebar,  /* 侧边栏 */
    CommonBackground,
  },
  setup() {
    const { t } = useI18n()
    const store = useStore()
    const activeMenuItem = computed(() => store.getters.history.workspaceHistory)
    const enableAdminFunction = computed(() => store.getters.enableAdminFunction)

    // 常用功能
    const normalMenuItems = [
      {
        name: 'portal',
        icon: Compass,
        label: t('view.workspace.Workspace.portal')
      }
    ]

    // 管理员功能
    const adminMenuItems = [
      {
        name: 'app-management',
        icon: Stopwatch,
        label: t('view.workspace.Workspace.app-management')
      },
      {
        name: 'user-management',
        icon: User,
        label: t('view.workspace.Workspace.user_management'),
      },
      {
        name: 'musiclib-management',
        icon: Files,
        label: t('view.workspace.Workspace.musiclib_management'),
      },
    ]

    onMounted(() => {
      navigator.toWorkspaceHistory()
    })

    return {
      t,
      navigator,
      authService,
      activeMenuItem,
      adminMenuItems,
      normalMenuItems,
      enableAdminFunction,
    }
  }
}
</script>
<template>
  <CommonBackground />
  <!-- 背景 -->
  <MusicatriNavbar />
  <!-- 导航栏 -->
  <div class="workspace">
    <div class="sidebar">
      <div class="sidebar-divider-text unselectable">
        {{ t('view.workspace.Workspace.quick_start') }}
      </div>
      <CommonSidebar
        :menu-items="normalMenuItems"
        :active-menu-item="activeMenuItem"
        :on-menu-item-selected="navigator.toWorkspace"
      />
      <!-- 管理员面板 -->
      <div class="sidebar-divider-text unselectable"
           v-if="enableAdminFunction">
        {{ t('view.workspace.Workspace.admin_function') }}
      </div>
      <CommonSidebar
        v-if="enableAdminFunction"
        :menu-items="adminMenuItems"
        :active-menu-item="activeMenuItem"
        :on-menu-item-selected="navigator.toWorkspace"
      />
    </div>
    <!-- 工作空间列表 -->
    <div class="content"><RouterView /></div>
    <!-- 功能面板 -->
  </div>
</template>
<style scoped>
.content {
  flex: 1; /* 填充剩余空间 */
  padding: 20px;
}

.workspace {
  display: flex;
}
</style>
