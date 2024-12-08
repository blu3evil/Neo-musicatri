<!-- 项目设置页面 -->
<script>
import MusicatriNavbar from '@/components/musicatri-navbar.vue'
import CommonBackground from '@/components/common-background.vue'
import CommonSidebar from '@/components/common-sidebar.vue'
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { Stopwatch, Promotion } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { navigator } from '@/router.js'

export default {
  components: {
    MusicatriNavbar /* 导航栏 */,
    CommonSidebar,  /* 侧边栏 */
    CommonBackground
  },
  setup() {
    // todo: 页面间距过窄时导航栏收缩
    const { t } = useI18n()
    const store = useStore()
    const activeWorkspaceMenuItem = computed(() =>
      store.getters.activeWorkspaceMenuItem)

    const onWorkspaceMenuItemSelected = (name) => {
      store.dispatch('setActiveWorkspaceMenuItem', name)
      if (name === 'dashboard') {
        navigator.toDashboardHistory()
      } else if (name === 'portal') {
        navigator.toPortal()
      } else navigator.toWorkspaceHistory()
    }

    // 管理员功能
    const adminWorkspaceMenuItems = [
      {
        name: 'dashboard',
        icon: Stopwatch,
        label: t('view.workspace.Workspace.dashboard')
      }
    ]

    // 常用功能
    const normalWorkspaceMenuItems = [
      {
        name: 'portal',
        icon: Promotion,
        label: t('view.workspace.Workspace.portal')
      }
    ]

    onMounted(async () => {
      await navigator.toWorkspaceHistory()  // 检索历史
    })

    return {
      t,
      activeWorkspaceMenuItem,
      adminWorkspaceMenuItems,
      normalWorkspaceMenuItems,
      onWorkspaceMenuItemSelected
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
        :menu-items="normalWorkspaceMenuItems"
        :active-menu-item="activeWorkspaceMenuItem"
        :on-menu-item-selected="onWorkspaceMenuItemSelected"
      />
      <div style="margin-top: 10px"></div>
      <div class="sidebar-divider-text unselectable">
        {{ t('view.workspace.Workspace.admin_function') }}
      </div>
      <CommonSidebar
        :menu-items="adminWorkspaceMenuItems"
        :active-menu-item="activeWorkspaceMenuItem"
        :on-menu-item-selected="onWorkspaceMenuItemSelected"
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
