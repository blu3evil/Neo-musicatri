<script>
import AtriStatusPanel from '@/components/atri-status-panel.vue'
import SystemStatusPanel from '@/components/system-status-panel.vue'
import { useStore } from 'vuex'
import { onMounted } from 'vue'

export default {
  components: {
    AtriStatusPanel /* 亚托莉状态面板 */,
    SystemStatusPanel  /* 服务端状态面板 */,
  },

  // todo: 按钮被选中样式修改

  setup() {
    const store = useStore()
    onMounted(() => {
      store.dispatch('setHistory', {
        name: 'appManagementHistory', history: 'overview'
      })
    })
  }
}



</script>
<template>
<!--  <el-row>-->
<!--    <el-col :span="24">-->
<!--      <AtriStatusPanel style="margin-top: 10px" />-->
<!--    </el-col>-->
<!--  </el-row>-->
</template>
<style scoped>

</style>
