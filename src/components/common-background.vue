<script>
import { ref } from 'vue'

export default {
  // todo: 设计一个可以点击的背景图片
  setup(props, { expose }) {
    const imageUrl = ref('')

    // 直接加载背景图
    const load = (url) => {
      imageUrl.value = url
    }

    // 异步加载背景图
    const loadAsync = url => {
      const img = new Image()
      img.src = url // 使用错误响应时的背景
      img.onload = () => (imageUrl.value = img.src) // 等待图片加载完成后再刷新
    }

    expose({
      load,
      loadAsync,
    })
    return {
      imageUrl,
    }
  }
}
</script>
<template>
  <div class="background"
       :style="{ backgroundImage: `url(${imageUrl})` }">
    <slot></slot>
  </div>
</template>
