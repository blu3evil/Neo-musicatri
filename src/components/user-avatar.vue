<!-- 用户头像 -->
<script>
import { computed } from 'vue'
import { useStore } from 'vuex'

export default {
  setup() {
    const store = useStore()
    const userAvatarURL = computed(() => store.getters.currentUserAvatarURL)
    return { userAvatarURL }
  }
}
</script>
<template>
  <el-avatar :src="userAvatarURL"><slot>'_>'</slot></el-avatar>
</template>
