<!-- 机器人当前状态面板 -->
<script>
import { ref } from 'vue'

export default {
  computed: {

  },
  components: {
  },
  setup() {
    const percentage = ref(20)
    return {
      percentage,
    }
  }
}
</script>
<template>
  <el-card class="unselectable" style="height: 200px">
    <template #header class="header">
      <div class="card-header">
        <span>服务端状态</span>
      </div>
    </template>

    <div class="content">
      <div class="common-layout">
        <el-container>
          <el-aside width="140px">  <!-- 状态进度条 -->
            <el-progress type="circle"
                         status="success"
                         :percentage="100">
              <template #default="{ percentage }">
                <span class="percentage-label">运行中</span>
              </template>
            </el-progress>
          </el-aside>

          <el-main style="transform: translateY(-16px)">  <!-- 状态框体 -->
            <div>h1</div>
            <div>h1</div>
            <div>h1</div>
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

.content {
  color: vaR(--text-color-2)
}

.card-header {
  font-size: var(--text-small);
  color: var(--text-color);
  height: 20px;
}
</style>
