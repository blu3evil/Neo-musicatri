<script>
export default {
  // todo: 设计一个可以点击的背景图片
  setup() {
  }
}
</script>
<template>
  <div class="background"><slot></slot></div>
</template>
<style scoped>
.background {
  background-image: url('/src/assets/user-login/ev000al.jpg');
}
</style>
