<!-- 用户头像 -->
<script>
import { Loading, Refresh } from '@element-plus/icons-vue'
import { computed } from 'vue'
import { AvatarStatus } from '@/status.js'
import { useStore } from 'vuex'

export default {
  components: {
    Loading,
    Refresh,
  },
  props: {
    userAvatarContext: {
      type: Object,
      required: true,
    },
    clickToRefresh: {  /* 点击之后重新加载 */
      type: Boolean,
      required: false,
      default: false
    }
  },
  setup(props, { expose }) {
    const store = useStore()
    const context = computed(() => props.userAvatarContext)

    // const url = computed(() => {
    //   if (!props.userAvatarContext) {
    //     return ''
    //   } else {
    //     return props.userAvatarContext.url
    //   }
    // })

    const allowRefresh = computed(() =>
      [AvatarStatus.PREPARED, AvatarStatus.FAILED]
      .includes(context.value.status))
    const isLoading = computed(() => context.value.status === AvatarStatus.LOADING)

    const onClick = async () => {
      if (props.clickToRefresh && allowRefresh.value) {
        await store.dispatch('loadAvatar', { id: context.value.id })  // 加载用户头像
      }
    }

    return {
      // url,
      context,
      isLoading,
      allowRefresh,
      AvatarStatus,
      onClick,
    }
  },
}
</script>
<template>
  <el-avatar :src="context.url"
             v-loading="isLoading"
             @click="onClick"
             element-loading-background="transparent"
  >
    <div v-if="allowRefresh">'_>'</div>
  </el-avatar>
</template>
<style>
.el-loading-mask {
  transition: none;
  --el-color-primary: var(--text-color);
  line-height: 0;  /* 避免错位 */
}
</style>
