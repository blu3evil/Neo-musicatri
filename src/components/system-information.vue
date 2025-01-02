<script>
import LoadingString from '@/components/loading-string.vue'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'
import { useStore } from 'vuex'

export default {
  components: {
    LoadingString,
  },
  setup() {
    const { t } = useI18n()
    const store = useStore()
    const systemInfo = computed(() => store.getters.systemInfo)
    return {
      t,
      systemInfo,
    }
  }
}
</script>
<template>
  <!-- 服务端信息 -->
  <el-row style="margin-top: 40px">
    <el-col :span="24">
      <h2 class="unselectable">{{ t('view.AboutSetting.system_info') }}</h2>
    </el-col>
  </el-row>
  <el-row>
      <span class="text-small unselectable">
        {{ t('view.AboutSetting.system_name') }}:
        <LoadingString :message="systemInfo['name']" />
      </span>
  </el-row>
  <el-row>
      <span class="text-small unselectable">
        {{ t('view.AboutSetting.system_version') }}:
        <LoadingString :message="systemInfo['version']" />
      </span>
  </el-row>
  <el-row>
      <span class="text-small unselectable">
        {{ t('view.AboutSetting.system_description') }}:
        <LoadingString :message="systemInfo['description']" />
      </span>
  </el-row>
</template>
<style scoped></style>
