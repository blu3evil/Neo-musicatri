<!-- 项目设置页面 -->
<script>
import CommonNavbar from '@/components/common-navbar.vue'
import SettingSidebar from '@/components/setting-sidebar.vue'
import { RouterView } from 'vue-router'
export default {
  components: { CommonNavbar, SettingSidebar },
  setup() {
    // todo: 页面间距过窄时导航栏收缩
  }
}


</script>
<template>
  <div class="fullscreen-background" id="background" />  <!-- 背景 -->
  <CommonNavbar />  <!-- 导航栏 -->

  <div class="app-setting">
    <div class="sidebar">
      <SettingSidebar />
    </div>
    <div class="content">
      <RouterView />
    </div>
  </div>

</template>
<style scoped>
/* 背景图片 */
.fullscreen-background {
  position: fixed; /* 固定定位，覆盖全屏 */
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-size: cover; /* 使背景图覆盖整个容器 */
  background-position: center; /* 背景图居中 */
  background-repeat: no-repeat; /* 不重复背景图 */
  z-index: -1; /* 确保在其他内容下方 */
  background-color: var(--bg-color);
}

/* 侧边栏 */
.sidebar {
  margin-top: 30px;
  width: 260px;
  margin-right: 40px;
}

/* 设置页详情 */
.content {
  flex: 1;  /* 填充剩余空间 */
  padding: 20px;
}

.app-setting {
  display: flex;
}


</style>























