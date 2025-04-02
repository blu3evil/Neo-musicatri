<script>
import UserTablePanel from '@/components/user-management/user-table-panel.vue'
import { useStore } from 'vuex'
import { onMounted } from 'vue'

export default {
  components: {
    UserTablePanel,
  },
  setup() {
    const store = useStore()
    onMounted(() => {
      store.dispatch('setHistory', {
        name: 'userManagementHistory', history: 'management'
      })
    })
  }
}
</script>
<template>
  <UserTablePanel/>
</template>
<style scoped>
</style>
