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
      return new Promise((resolve, reject) => {
        const img = new Image()
        img.src = url
        img.onload = () => {
          // 预加载图片
          imageUrl.value = img.src
          resolve(imageUrl.value)
        }

        img.onerror = () => {
          // 图片加载失败
          reject(new Error('Image load failed'))
        }
      })
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
