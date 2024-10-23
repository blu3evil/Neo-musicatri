<!-- 设置侧边栏 -->
<!--suppress HtmlUnknownTarget -->
<script>
import {
  Document,
  Menu as IconMenu,
  Location,
  Setting,
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { computed, onMounted, ref } from 'vue' // 路由
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'

export default {
  components: {
    IconMenu,
    Document,
    Location,
    Setting,
  },
  setup() {
    const router = useRouter() // 路由
    const store = useStore() // 存储
    const { t } = useI18n() // 本地化

    // 通过vuex获取当前激活页面
    const activeSettingPage = computed(() => store.getters.activeSettingPage)
    const availableSettingPages = computed(() => store.getters.availableSettingPages)

    /**
     * 处理菜单点击事件，回调函数中传入不同菜单控件的index信息
     * @param index el-menu-item定义的index值
     */
    const handleMenuSelect = index => {
      store.commit('setActiveSettingPage', index) // 设置activeSettingPage属性
    }

    onMounted(() => {})

    return {
      handleMenuSelect,
      activeSettingPage,
      availableSettingPages,  // 可用激活页面列表
      router,
      t,
    }
  },
}
</script>

<template>

  <!-- 设置菜单 -->
  <el-menu
    default-active="2"
    class="setting-sidebar-menu"
    @select="handleMenuSelect">

    <el-menu-item
      index="appearance"
      :class="['menu-item', activeSettingPage === 'appearance'? 'is-active': '' ]"
      @click="router.push('/settings/appearance')">
      <el-icon>
        <icon-menu />
      </el-icon>
      <span>{{ t('component.setting-sidebar.appearance_setting') }}</span>
    </el-menu-item>

    <el-menu-item
      index="profile"
      :class="['menu-item', activeSettingPage === 'profile'? 'is-active': '' ]"
      @click="router.push('/settings/profile')">
      <el-icon>
        <UserFilled />
      </el-icon>
      <span>{{ t('component.setting-sidebar.profile_setting') }}</span>
    </el-menu-item>

  </el-menu>
</template>

<style scoped>
/* 侧边栏背景色 */

.el-menu {
  background-color: var(--bg-color);
  border: none; /* 去除分割线 */
  /*border-right: 2px solid var(--divider-color);*/
}

.router-link {
  text-decoration: none;
}

.menu-item {
  color: var(--text-color);
  font-size: var(--text-medium);
  user-select: none;
  border-radius: 8px;
  margin: 0 10px 0 10px;
}

/* 设置菜单选项被激活时的样式 */
.menu-item.is-active,
.menu-item.is-active:hover {
  background-color: var(--bg-color-2);
  border-radius: 8px;
}

.menu-item:hover {
  background-color: var(--bg-color);
}
</style>
