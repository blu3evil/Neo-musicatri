<script>

import CommonNavbar from '@/components/common-navbar.vue'
import CommonPanel from '@/components/common-panel.vue'
import CommonBackground from '@/components/common-background.vue'
import { useI18n } from 'vue-i18n'
import { onMounted, useTemplateRef } from 'vue'
import { useNavigateHelper } from '@/router.js'

export default {
  name: 'NotFound',
  components: {
    CommonNavbar /* 导航栏 */,
    CommonPanel /* 面板 */,
    CommonBackground /* 背景 */
  },

  setup() {
    const { t } = useI18n()  // 本地化
    const panelRef = useTemplateRef('panel-ref')
    const bgRef = useTemplateRef('bg-ref')
    const navigateHelper = useNavigateHelper()

    const initPanel = () => {
      bgRef.value.loadAsync('/src/assets/not-found/ev011cl.png')
      panelRef.value.setTitle(t('view.NotFound.title'))
      addReturnMainLink()
    }

    const addReturnMainLink = () => {
      panelRef.value.addLink({
        desc: t('view.NotFound.return_index'),
        click: () => navigateHelper.toUserIndex(),
        href: '/'
      })
    }

    onMounted(() => {
      initPanel()
    })
  }
}

</script>
<template>
  <CommonBackground ref="bg-ref" />
  <CommonNavbar />
  <CommonPanel ref="panel-ref" />
</template>
<style scoped>

</style>
