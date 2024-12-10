<script>
import { onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  setup() {
    const store = useStore()
    onMounted(() => {
      store.dispatch('setActiveDashboardMenuItem', 'users')
    })
  }
}
</script>
<template>
  <h1>User Management</h1>
</template>
<style scoped></style>
