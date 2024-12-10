<script>
import { onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  setup() {
    const store = useStore()
    onMounted(() => {
      store.dispatch('setActiveDashboardMenuItem', 'overview')
    })
  }
}
</script>
<template>
  <h1>Application Overview</h1>
</template>
<style scoped>

</style>
