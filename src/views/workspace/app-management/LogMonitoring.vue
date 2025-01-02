<script>
import { useStore } from 'vuex'
import { onMounted } from 'vue'

export default {
  setup() {
    const store = useStore()
    onMounted(() => {
      store.dispatch('setHistory', {
        name: 'appManagementHistory', history: 'logs'
      })
    })
  }
}
</script>

<template>
 <h1>Log Monitoring</h1>
</template>

<style scoped>

</style>
