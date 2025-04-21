<script>
import AtriStatusPanel from '@/components/atri-status-panel.vue'
import SystemStatusPanel from '@/components/system-status-panel.vue'
import { useStore } from 'vuex'
import { onMounted } from 'vue'

export default {
  components: {
  },

  setup() {
    const store = useStore()
    onMounted(() => {
      store.dispatch('setHistory', {
        name: 'botManagementHistory', history: 'overview'
      })
    })
  }
}



</script>
<template>
  <h1>Bot Overview</h1>
</template>
<style scoped>

</style>
