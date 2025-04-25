<script>
import SongTablePanel from '@/components/musiclib-management/song-table-panel.vue'
import { useStore } from 'vuex'
import { onMounted } from 'vue'

export default {
  components: {
    SongTablePanel,
  },
  setup() {
    const store = useStore()



    onMounted(() => {
      store.dispatch('setHistory', {
        name: 'musiclibManagementHistory', history: 'management'
      })
    })
  }
}
</script>
<template>
  <SongTablePanel/>
</template>
<style scoped>
</style>
