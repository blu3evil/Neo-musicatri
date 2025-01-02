<script>
import { useStore } from 'vuex'
import { onMounted } from 'vue'

export default {
  setup() {
    const store = useStore()
    onMounted(() => {
      store.dispatch('setHistory', {
        name: 'userManagementHistory', history: 'overview'
      })
    })
  }
}
</script>
<template>
  <h1>Users Overview</h1>
</template>
<style scoped>

</style>
