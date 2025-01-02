<script>

import MusicatriNavbar from '@/components/musicatri-navbar.vue'
import CommonPanel from '@/components/common-panel.vue'
import CommonBackground from '@/components/common-background.vue'
import { useI18n } from 'vue-i18n'
import { onMounted, useTemplateRef } from 'vue'
import { navigator } from '@/router.js'

export default {
  name: 'NotFound',
  components: {
    MusicatriNavbar /* 导航栏 */,
    CommonPanel /* 面板 */,
    CommonBackground /* 背景 */
  },

  setup() {
    const { t } = useI18n()  // 本地化
    const panelRef = useTemplateRef('panel-ref')
    const bgRef = useTemplateRef('bg-ref')

    const initPanel = () => {
      bgRef.value.loadAsync('/src/assets/not-found/ev011cl.png')
      panelRef.value.setTitle(t('view.NotFound.title'))
      addReturnMainLink()
    }

    const addReturnMainLink = () => {
      panelRef.value.appendEventLink(
        t('view.NotFound.return_index'),
        async () => await navigator.toWorkspaceHistory()
        )
    }

    onMounted(() => {
      initPanel()
    })
  }
}

</script>
<template>
  <CommonBackground ref="bg-ref" />
  <MusicatriNavbar />
  <CommonPanel ref="panel-ref" />
</template>
<style scoped>

</style>
