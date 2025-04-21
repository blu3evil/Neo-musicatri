<!-- 用户信息面板 -->
<script>
import UserAvatar from '@/components/user-avatar.vue'
import UserAvatarV2 from '@/components/user-avatar-v2.vue'
import { Tools, CloseBold } from '@element-plus/icons-vue'
import { Refresh, Loading } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import { computed } from 'vue'
import { navigator } from '@/router.js'
import { PopupMessage } from '@/utils/ui-helper.js'

export default {
  components: {
    UserAvatar /* 用户头像 */,
    UserAvatarV2,  /* 用户头像V2 */
    Tools /* element plus图标 */ ,
    CloseBold,
    Refresh,
    Loading,
  },
  setup() {
    const { t } = useI18n()
    const store = useStore()
    const currentUser = computed(() => store.getters.currentUser)
    const currentUserAvatarContext = computed(() => {
      const currentUser = store.getters.currentUser
      return store.getters.safeUserAvatarContexts(currentUser.id)
    })

    const onLogoutClick = () => {
      PopupMessage.warning(t('component.user-panel.confirm_logout'))
        .then(async () => {
          await store.dispatch('logoutCurrentUser')  // 执行用户登出
        }).catch(() => {})
    }

    return {
      t,
      navigator,
      currentUser,
      currentUserAvatarContext,
      onLogoutClick,
    }
  }
}
</script>
<template>
  <el-row>  <!-- 用户头像 -->
    <el-col :span="6">
      <UserAvatarV2 :user-avatar-context="currentUserAvatarContext"
                    class="user-avatar"
                    :click-to-refresh="true" />
    </el-col>
    <el-col :span="18">
      <div class="text-small" style="margin-top: 2px" >
        <el-row>{{currentUser.username}}</el-row>
        <el-row>id:{{currentUser.id}}</el-row>
      </div>
    </el-col>
  </el-row>

  <el-row style="margin-top: 15px">  <!-- 更多设置 -->
    <el-col :span="24"><div class="text-mini" >
      <a href="/" class="slide-animation-a" @click.prevent="navigator.toSettingsHistory()">
        <el-icon class="optional-icon"><Tools /></el-icon>
        <span class="optional-label">{{t('component.user-panel.more_settings')}}</span>
      </a>
    </div></el-col>
  </el-row>

  <el-row>  <!-- 登出 -->
    <el-col :span="24"><div class="text-mini" >
      <a href="/" class="slide-animation-a" @click.prevent="onLogoutClick">
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
