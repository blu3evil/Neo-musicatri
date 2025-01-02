<script>
import { onMounted, ref, watch, computed, onUnmounted } from 'vue'
export default {
  props: {
    message: {
      type: String,
      default: '',
      required: false,
    },
    ellipsis: {
      type: Boolean,
      required: false,
      default: false
    },
    interval: {
      type: Number,
      required: false,
      default: 500
    },
    ellipsisLength: {
      type: Number,
      required: false,
      default: 4
    }
  },
  setup(props) {
    const ellipsisStr = ref('.')  // 字符串加载动画
    let ellipsisIntervalId = ref('')
    const message = computed(() => props.message)
    const ellipsis = computed(() => props.ellipsis)

    const reloadEllipsis = () => {
      // 设置字符串循环
      clearTimeout(ellipsisIntervalId)
      if (props.ellipsis) {
        ellipsisStr.value = '.'
        ellipsisIntervalId = setInterval(() => {
          ellipsisStr.value = ellipsisStr.value.length < props.ellipsisLength ?
            ellipsisStr.value + '.' : '.'
        }, props.interval)
      }
    }

    onMounted(() => {
      reloadEllipsis()
    })

    onUnmounted(() => {
      clearTimeout(ellipsisIntervalId)
    })

    watch(message, (newVal, oldVal) => {
      ellipsisStr.value = '.'
    })

    watch(ellipsis, (newVal, oldVal) => {
      reloadEllipsis()
    })

    return { ellipsisStr }
  }
}
</script>
<template>
  <span>{{ message }}</span><span v-if="ellipsis">{{ ellipsisStr }}</span>
</template>
<style scoped></style>
