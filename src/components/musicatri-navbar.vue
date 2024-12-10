<!--suppress JSUnresolvedReference -->
<script>
import UserPanel from '@/components/user-panel.vue'
import UserAvatar from '@/components/user-avatar.vue'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import { navigator } from '@/router.js'
import { Tools, Loading } from '@element-plus/icons-vue'
import { authService } from '@/services/auth-service.js'

export default {
  components: {
    UserPanel /* 用户信息面板 */,
    UserAvatar /* 用户头像 */,
    Tools ,
    Loading,
  },
  setup() {
    const { t } = useI18n()  // 本地化
    const store = useStore()  // 存储
    const isAvatarActive = ref(false)
    const userSocketStatus = computed(() => store.getters.userSocketStatus)
    const userLoginStatus = computed(() => authService.verifyLogin())

    return {
      userLoginStatus,
      userSocketStatus,
      isAvatarActive,
      navigator,
      t, // 本地化
    }
  },
}
</script>

<template>
  <el-menu
    class="user-navbar unselectable"
    mode="horizontal"
    :ellipsis="false"
  >
    <!-- musicatriLOGO -->
    <el-menu-item index="0" @click="navigator.toWorkspace()">
      <img
        style="width: 150px; margin-bottom: 2px"
        src="/src/assets/common-navbar/navbar-logo.png"
        alt="Element logo"
      />
      <h1 id="navbar-title" style="margin-top: 6px">Musicatri</h1>
    </el-menu-item>

    <!-- 用户头像 -->
    <el-menu-item index="1" v-if="userLoginStatus">
      <el-popover
        placement="bottom-start"
        :width="340"
        trigger="click"
        @show="isAvatarActive = true"
        @hide="isAvatarActive = false"
      >
        <template #reference>
          <UserAvatar :class="{ active: isAvatarActive, 'user-avatar': true }"
                      @click="isAvatarActive = !isAvatarActive"
                      :allow-refresh="false"
                      text-style="margin-top: 4px"
                      icon-style="margin-left: 5px; margin-bottom: 1px"/>
        </template>
        <UserPanel />
      </el-popover>
    </el-menu-item>
  </el-menu>
</template>


<style scoped>
/* 菜单栏按钮右对齐 */
.el-menu--horizontal > .el-menu-item:nth-child(1) {
  margin-right: auto
}

/* 菜单栏按钮悬停 */
.el-menu--horizontal .el-menu-item:not(.is-disabled):focus,
.el-menu--horizontal .el-menu-item:not(.is-disabled):hover {
  background-color: transparent; /* 隐藏按钮悬停背景色 */
}

/* 菜单栏按钮激活时 */
.el-menu--horizontal > .el-menu-item.is-active {
  border-bottom: none;
  border-bottom: transparent; /* 隐藏底边色 */
  color: #4b5c6e !important;
}

/* 导航栏 */
.el-menu {
  background-color: var(--navbar-bg-color);
  border: none; /* 隐藏导航栏底边 */
  height: 75px;
}

/* 菜单栏按钮取消底栏 */
.el-menu--horizontal > .el-menu-item {
  border: none;
  height: 100%;
  margin: 0;
}

/* 导航栏标题 */
#navbar-title {
  font-size: var(--text-large);
  font-weight: bold;
}

/* 导航栏标题字色 */
.el-menu--horizontal > .el-menu-item {
  color: var(--navbar-color);
}

/* 导航栏标题激活时字色 */
.el-menu--horizontal > .el-menu-item.is-active {
  border-bottom: transparent;
  color: var(--navbar-color) !important;
}

/* 阻止默认hover效果 */
.el-menu-item:hover {
  background-color: transparent !important; /* 设置为透明或您想要的颜色 */
  color: inherit !important; /* 保持文本颜色 */
}

/* 用户头像 */
.user-avatar {
  background-color: var(--bg-color);
  color: var(--text-color);
  font-size: var(--text-small);
  width: 42px;
  height: 42px;
  margin-bottom: 3px;
  transition: box-shadow 0.3s ease-in-out, background-color 0.3s ease-in-out;
}

/* 头像框悬停事件 */
.user-avatar:hover {
  background-color: var(--popper-bg-color);
  box-shadow: 0 0 0 4px var(--popper-bg-color);
}

.user-avatar.active {
  background-color: var(--popper-bg-color);
  box-shadow: 0 0 0 4px var(--popper-bg-color);
}

</style>
