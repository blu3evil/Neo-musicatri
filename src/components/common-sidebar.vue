<!-- 设置侧边栏 -->
<!--suppress HtmlUnknownTarget -->
<script>
import { computed, h, onMounted, ref } from 'vue' // 路由
import { ElIcon } from 'element-plus'

export default {
  props: {
    activeMenuItem: {
      type: String,
      required: true,
    },
    menuItems: {
      type: Array,
      required: true,
    },
    onMenuItemSelected: {
      type: Function,
      required: true,
    }
  },
  setup(props) {
    // 通过vuex获取当前激活页面
    const items = ref([])
    const isActive = computed((name) => {
      return props.activeMenuItem === name ? 'active' : ''
    })
    onMounted(() => {
      props.menuItems.forEach(item => {
        items.value.push({
          name: item.name,
          icon: h(ElIcon, null, { default: () => h(item.icon) }),
          label: item.label
        })
      })
    })
    return { items, isActive }
  }
}
</script>

<template>
  <!-- 设置菜单 -->
  <el-menu class="setting-sidebar-menu">
    <el-menu-item
      v-for="(item) in items"
      :index="item['name']"
      :class="['menu-item', activeMenuItem === item['name'] ? 'active' : '']"
      @click="onMenuItemSelected(item['name'])">
      <component :is="item['icon']" />
      <span>{{item['label']}}</span>
    </el-menu-item>
  </el-menu>
</template>

<style scoped>
/* 侧边栏背景色 */
.el-menu {
  background-color: transparent;
  border: none; /* 去除分割线 */
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
  height: 50px;
}

.menu-item.active {
  background-color: var(--bg-color-2) !important;
  border-radius: 8px !important;
}

/* 设置菜单选项被激活时的样式 */
.menu-item.is-active,
.menu-item.is-active:hover {
  background-color: transparent;
  border-radius: 8px;
}

.menu-item:hover {
  background-color: var(--bg-color);
}
</style>
