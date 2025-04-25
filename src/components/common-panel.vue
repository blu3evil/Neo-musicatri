<!-- 授权结果信息回显 -->
<script>
export default {
  props: ['header_style', 'body_style', 'footer_style'],
  setup() {
    return {

    }
  }
}
</script>

<template>
  <el-card class="unselectable">
    <template #header>
      <slot name="header"></slot>
    </template>
    <slot></slot>  <!-- 默认插槽 -->
    <template #footer>
      <slot name="footer"></slot>
    </template>
  </el-card>
</template>
<style>
/* 卡片头 */
.el-card__header {
  /*border-bottom: 1px solid var(--divider-color) !important;*/
  border: none;
  padding: 0 0 0 0;
}

/* 卡片体 */
.el-card__body {
  padding: 0 0 0 0;
  flex: 1;
}

/* 卡片底 */
.el-card__footer {
  padding: 0 0 0 0;
}

.el-card {
  --el-card-border-color: none;
  display: flex;
  flex-direction: column;
  border: 1px;
  color: var(--text-color); /* 使用主题字色 */
  background-color: var(--redirect-card-bg-color); /* 背景色 */
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.7); /* 阴影效果 */
  border-radius: var(--border-radius);
}
</style>
