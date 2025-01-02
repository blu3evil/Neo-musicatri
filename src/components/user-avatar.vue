<!-- 用户头像 -->
<script>
import { useStore } from 'vuex'
import { computed, watch } from 'vue'
import { Loading, Refresh } from '@element-plus/icons-vue'
import { userService } from '@/services/user-service.js'
import { useI18n } from 'vue-i18n'

export default {
  components: {
    Loading,
    Refresh,
  },
  props: {
    allowRefresh: {  // 是否允许在头像初始化失败的情况下点击刷新
      type: Boolean,
      required: false,
      default: false
    },
    textStyle: {  // 文本占位符的css样式
      type: String,
      required: false,
      default: ''
    },
    iconStyle: {  // 图标占位符的css样式
      type: String,
      required: false,
      default: ''
    }
  },
  setup(props) {
    const { t } = useI18n()
    const store = useStore()
    const userAvatarURL = computed(() => store.getters.userAvatarURL)
    const userSocketStatus = computed(() => store.getters.userSocketStatus)
    const userAvatarStatus = computed(() => store.getters.userAvatarStatus)

    const onAvatarClick = async () => {
      if (props.allowRefresh
        && userAvatarURL.value === null
        && userAvatarStatus.value === 'unset' ) {
        store.dispatch('loadUserAvatar').then()
      }
    }

    // 在用户每次建立连接的时候初始化头像
    watch(userSocketStatus, async (newVal, oldVal) => {
      if (newVal === 'connected') {
        store.dispatch('loadUserAvatar').then()
      }
    })

    return {
      userAvatarURL,
      onAvatarClick,
      userAvatarStatus,
    }
  }
}
</script>
<template>
  <el-avatar :src="userAvatarURL" @click="onAvatarClick">
    <div v-if="userAvatarURL === null">
      <div v-if="userAvatarStatus === 'unset'">
        <el-icon v-if="allowRefresh" :style="iconStyle">
          <Refresh/>
        </el-icon>
        <div v-else :style="textStyle">'_>'</div>
      </div>

      <div v-if="userAvatarStatus === 'loading'">
        <el-icon class="is-loading" :style="iconStyle">
          <Loading/>
        </el-icon>
      </div>
    </div>
  </el-avatar>
</template>
