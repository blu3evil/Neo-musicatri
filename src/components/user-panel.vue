<!-- 用户信息面板 -->
<script>
import UserAvatar from '@/components/user-avatar.vue'
import { Tools, CloseBold } from '@element-plus/icons-vue'
import { Refresh, Loading } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import { computed } from 'vue'
import { navigator } from '@/router.js'
import { PopupMessage, ToastMessage } from '@/utils/ui-helper.js'
import { authService } from '@/services/auth-service.js'
import { userSocketContext } from '@/sockets/user-socket.js'
import { adminSocketContext } from '@/sockets/admin-socket.js'

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

    const onLogoutClick = () => {
      PopupMessage.warning(t('component.user-panel.confirm_logout'))
        .then(async () => {
          // 执行用户登出
          const result = await authService.userLogout()
          if (result.isSuccess()) {  // 登出成功
            // 断开user socket连接
            const result1 = await userSocketContext.disconnect()
            if (!result1.isSuccess()) ToastMessage.error(result.message)
            // 断开admin socket连接
            const result2 = await adminSocketContext.disconnect()
            if (!result2.isSuccess()) ToastMessage.error(result.message)
            // 清除用户数据
            await store.dispatch('clearCurrentUser')
            await navigator.toLogin()  // 跳转到login页面
          } else {
            ToastMessage.error(result.message)  // 登出失败
          }
        }).catch(() => {})
    }

    return {
      t,
      navigator,
      currentUser,
      onLogoutClick,
    }
  }
}
</script>
<template>
  <el-row>  <!-- 用户头像 -->
    <el-col :span="6"><div class="text-small" >
      <UserAvatar class="user-avatar"
                  :allow-refresh="true"
                  icon-style="margin-top: 9px" />
    </div></el-col>
    <el-col :span="18"><div class="text-small" style="margin-top: 6px" >
      <el-row>{{currentUser.username}}</el-row>
      <el-row>id:{{currentUser.id}}</el-row>
    </div></el-col>
  </el-row>

  <el-row style="margin-top: 15px">  <!-- 更多设置 -->
    <el-col :span="24"><div class="text-mini" >
      <a href="/" class="slide-animation-a" @click.prevent="navigator.toSettingHistory()">
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
