<!-- 设置侧边栏 -->
<!--suppress HtmlUnknownTarget -->
<script>
import {
  Document,
  Menu as IconMenu,
  Location,
  Setting,
  UserFilled,
  InfoFilled,
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { computed, onMounted, h } from 'vue' // 路由
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { ElIcon } from 'element-plus'

export default {
  components: {
    IconMenu,
    Document,
    Location,
    Setting,
    InfoFilled,
  },
  setup() {
    const router = useRouter() // 路由
    const store = useStore() // 存储
    const { t } = useI18n() // 本地化

    // 通过vuex获取当前激活页面
    const activeSettingPage = computed(() => store.getters.activeSettingPage)

    /**
     * 处理菜单点击事件，回调函数中传入不同菜单控件的index信息
     * @param index el-menu-item定义的index值
     */
    const handleMenuSelect = index => {
      store.commit('setActiveSettingPage', index) // 设置activeSettingPage属性
    }

    const items = [
      {
        name: 'appearance',
        path: '/settings/appearance',
        icon: h(ElIcon, null, { default: () => h(IconMenu) }),
        span: t('component.setting-sidebar.appearance_setting')
      },
      {
        name: 'profile',
        path: '/settings/profile',
        icon: h(ElIcon, null, { default: () => h(UserFilled) }),
        span: t('component.setting-sidebar.profile_setting')
      },
      {
        name: 'about',
        path: '/settings/about',
        icon: h(ElIcon, null, { default: () => h(InfoFilled) }),
        span: t('component.setting-sidebar.about_setting')
      }
    ]

    onMounted(() => {})

    return {
      handleMenuSelect,
      activeSettingPage,
      router,
      t,
      items,
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
      v-for="(item, index) in items"
      :index="item['name']"
      :class="['menu-item', activeSettingPage === item['name']? 'is-active': '' ]"
      @click="router.push(item['path'])">
      <component :is="item['icon']" />
      <span>{{item['span']}}</span>
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
