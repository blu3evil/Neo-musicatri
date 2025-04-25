<!-- 管理员功能启用关闭 -->
<script>
import { useI18n } from 'vue-i18n'
import { computed, ref } from 'vue'
import { useStore } from 'vuex'
import { globalEventbus } from '@/mitt/global-eventbus.js'
import { authServiceV1 } from '@/services/auth-service.js'
import { Events } from '@/events.js'

export default {
  setup() {
    const { t } = useI18n()
    const store = useStore()
    const isLoading = ref(false)

    const enableAdminFunction = computed({  // 显示管理员功能
      get() { return store.getters.enableAdminFunction },
      async set(value) {
        // 请求后端查询是否有对应的权限
        isLoading.value = true
        const result = await authServiceV1.verifyRole('admin')  // 校验管理员权限
        if (result.isSuccess()) {  // 允许提权
          globalEventbus.emit(value?
            Events.MITT.ADMIN_FUNCTION.ENABLE.SUCCESS:
            Events.MITT.ADMIN_FUNCTION.DISABLE.SUCCESS)
          await store.dispatch('setAdminFunctionStatus', value)
        } else {  // 禁止提权
          globalEventbus.emit(value?
            Events.MITT.ADMIN_FUNCTION.ENABLE.FAILED :
            Events.MITT.ADMIN_FUNCTION.DISABLE.FAILED, result.message)
        }
        isLoading.value = false  // 取消等待状态
      }
    })

    return {
      t,
      isLoading,
      enableAdminFunction,
    }
  },
}
</script>

<template>
  <!-- 开启管理员功能 -->
  <el-row style="margin-top: 20px">
    <span class="text-small unselectable">
      {{ t('view.AboutSetting.admin_function') }}
        <el-switch
          v-model="enableAdminFunction"
          size="large"
          style="margin-bottom: 6px"
          :loading="isLoading"
        />
    </span>
  </el-row>
</template>

<style scoped>

</style>
