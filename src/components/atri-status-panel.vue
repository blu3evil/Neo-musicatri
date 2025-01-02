<!-- 机器人当前状态面板 -->
<script>
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { atriService } from '@/services/atri-service.js'

export default {
  setup() {
    const { t } = useI18n()
    const store = useStore()
    const atriStatus = computed(() => store.getters.atriInfo.status)
    const atriStatusStr = computed(() => {  // 本地化
      switch (atriStatus.value) {
        case 'failed': return t('component.atri-status-panel.atri_failed')
        case 'stopped': return t('component.atri-status-panel.atri_stopped')
        case 'started': return t('component.atri-status-panel.atri_started')
        case 'starting': return t('component.atri-status-panel.atri_starting')
        case 'stopping': return t('component.atri-status-panel.atri_stopping')
      }
    })
    const launchBtnEnable = computed(() => {
      return !(atriStatus.value === 'stopped' || atriStatus.value === 'started')
    })

    // 启动或停止亚托莉
    const onLaunchBtnClick = async () => {
      const result = await store.dispatch('startAtri')
      console.log(result)
    }

    onMounted(() => {
      store.dispatch('loadAtriStatus')
    })
    return {
      atriStatusStr,
      atriStatus,
      launchBtnEnable,
      onLaunchBtnClick,
    }
  }
}
</script>
<template>
  <el-card class="unselectable" style="height: 200px">
    <template #header class="header">
      <div class="card-header">
        <span>亚托莉状态</span>
      </div>
    </template>

    <div class="content">
      <div class="common-layout">
        <el-container>
          <el-aside width="140px">  <!-- 状态进度条 -->
            <el-progress type="circle"
                         status="exception"
                         :percentage="100">
              <template #default="{ percentage }">
                <span class="percentage-label">{{ atriStatusStr }}</span>
              </template>
            </el-progress>
          </el-aside>

          <el-main style="transform: translateY(-16px)">  <!-- 状态框体 -->
            <div>
              <el-button type="primary"
                         style="width: 120px;
                         font-size: var(--text-mini);"
                         :loading="launchBtnEnable"
                         @click="onLaunchBtnClick">
                启动
              </el-button>
            </div>
          </el-main>
        </el-container>
      </div>
    </div>
  </el-card>
</template>
<style scoped>
.el-card {
  background-color: var(--bg-color-2);
  border-radius: var(--border-radius);
  border: none;
}

.percentage-label {
  font-size: var(--text-mini) !important;
}

.content {
  color: vaR(--text-color-2)
}

.card-header {
  font-size: var(--text-small);
  color: var(--text-color);
  height: 20px;
}
</style>
