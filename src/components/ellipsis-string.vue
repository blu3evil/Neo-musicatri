<script>
import { onMounted, ref, watch, computed } from 'vue'

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

    onMounted(() => {
      // 设置字符串循环
      ellipsisIntervalId = setInterval(() => {
        ellipsisStr.value = ellipsisStr.value.length < props.ellipsisLength ?
          ellipsisStr.value + '.' : '.'
      }, props.interval)
    })

    watch(message, (newVal, oldVal) => {
      ellipsisStr.value = '.'
    })

    return { ellipsisStr }
  }
}
</script>
<template>
  <span>{{ message }}</span><span v-if="ellipsis">{{ ellipsisStr }}</span>
</template>
<style scoped></style>
