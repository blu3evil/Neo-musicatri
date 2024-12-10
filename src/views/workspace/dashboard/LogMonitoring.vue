<script>
import { onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  setup() {
    const store = useStore()
    onMounted(() => {
      store.dispatch('setActiveDashboardMenuItem', 'logs')
    })
  }
}
</script>

<template>
 <h1>Log Monitoring</h1>
</template>

<style scoped>

</style>
