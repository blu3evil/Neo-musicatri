<script>
import { onMounted, ref } from 'vue'
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
    onMounted(() => {
      props.menuItems.forEach(item => {
        items.value.push({
          name: item.name,
          span: item.span
        })
      })
    })
    return { items }
  }
}
</script>
<template>
  <el-menu class="workspace-navbar unselectable"
           mode="horizontal" :ellipsis="false">
    <el-menu-item
      v-for="(item) in items"
      :index="item['name']"
      :class="['menu-item', activeMenuItem === item['name']? 'is-active': '' ]"
      @click="onMenuItemSelected(item['name'])">
      <span>{{item['span']}}</span>
    </el-menu-item>
  </el-menu>
</template>
<style scoped>
/* 导航栏本身 */
.el-menu {
  background-color: var(--navbar-bg-color);
  border-radius: 8px;
  margin-top: 10px;
  height: 50px;
}

/* 导航栏被激活的选项 */
.el-menu--horizontal>.el-menu-item.is-active {
  background-color: transparent;
  color: var(--text-active-color) !important;
}

.el-menu--horizontal>.el-menu-item:hover {
  color: transparent;
}

.el-menu--horizontal>.el-menu-item {
  border-bottom: none;
  color: var(--text-color) !important;
  font-size: var(--text-small);
}

/* 导航栏底部 */
.el-menu--horizontal.el-menu {
  border-bottom: none;
}

.el-menu--horizontal .el-menu-item:not(.is-disabled):focus,
.el-menu--horizontal .el-menu-item:not(.is-disabled):hover {
  background-color: transparent;
}
</style>
