<!-- 用户信息面板 -->
<script>
import UserAvatar from '@/components/user-avatar.vue'
import { Tools, CloseBold } from '@element-plus/icons-vue'
import { Refresh, Loading } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import { computed } from 'vue'
import { navigator } from '@/router.js'

export default {
  components: {
    UserAvatar /* 用户头像 */,
    Tools /* element plus图标 */ ,
    CloseBold,
    Refresh,
    Loading,
  },
  setup() {
    const { t } = useI18n()
    const store = useStore()
    const currentUser = computed(() => store.getters.currentUser)
    const currentAvatarURL = computed(() => store.getters.currentUserAvatarURL)
    const isCurrentUserAvatarLoading = computed(() => store.getters.isCurrentUserAvatarLoading)

    const onRefreshUserAvatarClick = async () => {
      if (currentAvatarURL.value !== null) return  // URL已经存在
      if (isCurrentUserAvatarLoading.value) return  // 当前头像正在加载，防抖
      // 重新初始化用户头像
      await store.dispatch('initCurrentAvatar', currentUser.value)
    }

    return {
      t,
      currentUser,
      currentAvatarURL,
      isCurrentUserAvatarLoading,
      onRefreshUserAvatarClick,
      navigator
    }
  }
}
</script>
<template>
  <el-row>  <!-- 用户头像 -->
    <el-col :span="6"><div class="text-small" >
      <UserAvatar class="user-avatar" @click="onRefreshUserAvatarClick">
        <el-icon v-if="!isCurrentUserAvatarLoading && currentAvatarURL === null">
          <Refresh/>
        </el-icon>
        <el-icon v-if="isCurrentUserAvatarLoading && currentAvatarURL === null"
                 class="is-loading">
          <Loading/>
        </el-icon>
      </UserAvatar>
    </div></el-col>
    <el-col :span="18"><div class="text-small" style="margin-top: 6px" >
      <el-row>{{currentUser.username}}</el-row>
      <el-row>id:{{currentUser.id}}</el-row>
    </div></el-col>
  </el-row>

  <el-row style="margin-top: 15px">  <!-- 更多设置 -->
    <el-col :span="24"><div class="text-mini" >
      <a href="/" class="slide-animation-a" @click.prevent="navigator.toSetting()">
        <el-icon class="optional-icon"><Tools /></el-icon>
        <span class="optional-label">{{t('component.user-panel.more_settings')}}</span>
      </a>
    </div></el-col>
  </el-row>

  <el-row>  <!-- 登出 -->
    <el-col :span="24"><div class="text-mini" >
      <a href="/" class="slide-animation-a">
        <el-icon class="optional-icon"><CloseBold /></el-icon>
        <span class="optional-label">{{t('component.user-panel.account_logout')}}</span>
      </a>
    </div></el-col>
  </el-row>
</template>
<style>
.user-avatar {
  width: 70px;
  height: 70px;
  background-color: var(--bg-color);
  font-size: var(--text-mini);
  color: var(--text-color);
}

.optional-icon {
  position: absolute;
  margin-top: 3px;
}

.optional-label {
  margin-left: 20px
}
</style>
