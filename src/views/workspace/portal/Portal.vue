<script>
import { onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  setup() {
    const store = useStore()
    onMounted(() => {
      store.dispatch('setActiveWorkspaceMenuItem', 'portal')
    })
  }
}
</script>

<template>
  <h1>Portal</h1>
</template>

<style scoped>

</style>
