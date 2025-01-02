<!-- 项目设置页面 -->
<script>
import MusicatriNavbar from '@/components/musicatri-navbar.vue'
import CommonBackground from '@/components/common-background.vue'
import CommonSidebar from '@/components/common-sidebar.vue'
import { navigator } from '@/router.js'
import { CircleClose } from '@element-plus/icons-vue'
import { computed } from 'vue'
import { useStore } from 'vuex'
import {
  Menu as IconMenu,
  UserFilled,
  InfoFilled,
} from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'

export default {
  components: {
    MusicatriNavbar /* 导航栏 */ ,
    CommonBackground  /* 背景 */,
    CommonSidebar /* 侧边栏 */,
    CircleClose
  },
  setup() {
    // todo: 页面间距过窄时导航栏收缩
    const { t } = useI18n()
    const store = useStore()
    const activeMenuItem = computed(
      () => store.getters.history.settingsHistory)

    const settingMenuItems = [
      {
        name: 'appearance',
        icon: IconMenu,
        label: computed(() => t('component.setting-sidebar.appearance_setting'))
      },
      {
        name: 'profile',
        icon: UserFilled,
        label: computed(() => t('component.setting-sidebar.profile_setting'))
      },
      {
        name: 'about',
        icon: InfoFilled,
        label: computed(() => t('component.setting-sidebar.about_setting'))
      }
    ]

    return {
      t,
      navigator,
      settingMenuItems,
      activeMenuItem,
    }
  }
}

</script>
<template>
  <CommonBackground />
  <MusicatriNavbar />  <!-- 导航栏 -->

  <div class="app-setting">  <!-- 侧边栏 -->
    <div class="sidebar">
      <div class="sidebar-divider-text unselectable">
        {{ t('component.setting-sidebar.atri_setting') }}
      </div>
      <CommonSidebar
        :menu-items="settingMenuItems"
        :active-menu-item="activeMenuItem"
        :on-menu-item-selected="navigator.toSettings" />
    </div>

    <div class="content"><RouterView /></div>  <!-- 设置面板 -->
    <div class="close-btn-area unselectable">
      <el-icon class="close-btn" size="42px"
               @click="navigator.toWorkspaceHistory()">
        <CircleClose />
      </el-icon>
    </div>
  </div>
<!--  <el-backtop :right="100" :bottom="100" />-->  <!-- todo: 可能的回到顶部按钮 -->
</template>
<style scoped>
/* 设置页详情 */
.content {
  flex: 1;  /* 填充剩余空间 */
  padding: 20px;
}

/* 关闭设置按钮 */
.close-btn-area {
  width: 81px;
  padding: 20px
}

/* 关闭按钮 */
.close-btn {
  color: var(--text-color);
  transition: color 0.3s ease-in-out;
}

.close-btn:hover {
  color: var(--text-active-color);
}

.app-setting {
  display: flex;
}
</style>










