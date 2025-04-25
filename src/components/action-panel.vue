<script>
import CommonPanel from '@/components/common-panel.vue'
import EllipsisString from '@/components/ellipsis-string.vue'
import { useI18n } from 'vue-i18n'
import { ref } from 'vue'
export default {
  components: {
    EllipsisString,
    CommonPanel,
  },
  setup(props, { expose }) {
    const { t } = useI18n() // 本地化
    const panelTitle = ref('') // 标题

    const panelEllipsisDisplay = ref(false) // 加载字符串显示
    const panelSubtitle = ref('') // 子标题

    const panelLinks = ref([]) // 所有可用连接
    const panelMessage = ref('') // 消息
    const isErrorMessage = ref(false) // 是否为错误消息

    /**
     * 设置panel标题
     * @param title 标题内容
     * @param ellipsisDisplay 是否显式标题末尾的字符串加载动画
     */
    const setTitle = (title, ellipsisDisplay=false) => {
      panelTitle.value = title
      panelEllipsisDisplay.value = ellipsisDisplay
    }

    /**
     * 设置panel的子标题
     * @param subtitle 子标题内容
     */
    const setSubtitle = subtitle => {
      panelSubtitle.value = subtitle
    }

    /**
     * 设置消息，默认为成功消息，通过_errorMessage来将消息设置为错误消息
     * @param message 消息内容
     * @param isError 是否为错误消息，默认值为false
     */
    const setMessage = (message, isError = false) => {
      panelMessage.value = message
      isErrorMessage.value = isError
    }

    // 添加一条链接
    const addLink = linkItem => {
      panelLinks.value.push(linkItem)
    }

    /* 添加事件链接 */
    const appendEventLink = (name, event) => {
      panelLinks.value.push({
        desc: name,
        href: '/',
        target: null,
        click: event
      })
    }

    /* 添加跳转链接 */
    const appendHrefLink = (name, href, isBlank=true) => {
      panelLinks.value.push({
        desc: name,
        href: href,
        target: isBlank? '_blank' : null,
        click: null
      })
    }

    // 清除标题，如果在状态中调用了这个方法应该在fadeout中调用同样的方法来清除
    const clearTitle = () => {
      panelTitle.value = ''
      panelSubtitle.value = ''
      panelEllipsisDisplay.value = false
    }

    const clearLinks = () => {
      panelLinks.value = []
    }

    // 清除消息
    const clearMessage = () => {
      panelMessage.value = ''
    }

    // 将方法暴露到外部
    expose({
      setTitle,
      setSubtitle,
      setMessage,
      addLink,
      appendEventLink,
      appendHrefLink,
      clearTitle,
      clearLinks,
      clearMessage,
    })

    return {
      t,
      title: panelTitle,
      subtitle: panelSubtitle, // 子标题
      ellipsisDisplay: panelEllipsisDisplay,
      message: panelMessage,
      isError: isErrorMessage,
      links: panelLinks,
    }
  },
}
</script>
<template>
  <div class="action-panel">
    <CommonPanel>
      <template #header>
        <div class="card-header">
          <h2>
            <EllipsisString :message="title" :ellipsis="ellipsisDisplay" />
          </h2>
          {{ subtitle }}
        </div>
      </template>

      <h3 class="text-error" v-if="isError">{{ message }}</h3>
      <h3 class="text-success" v-if="!isError">{{ message }}</h3>
      <div v-for="link in links">
        <a
          class="slide-animation-a"
          :href="link['href']"
          :target="link['target']"
          v-if="link['click'] == null"
        >
          <!-- 超链接 -->
          {{ link['desc'] }}
          <!-- 链接描述 -->
        </a>
        <a
          class="slide-animation-a"
          :href="link['href']"
          :target="link['target']"
          v-if="link['click'] != null"
          @click.prevent="link['click']"
        >
          <!-- 事件链接 -->
          {{ link['desc'] }}
        </a>
      </div>

      <template #footer>
        <div>
          {{ t('component.pending-panel.footer') }}
        </div>
      </template>
    </CommonPanel>
  </div>
</template>
<style>
.action-panel .el-card {
  height: 300px;
  width: 800px;
}

.action-panel .el-card__header {
  padding: 10px 0 0 10px;
}

.action-panel .el-card__body {
  padding: 0 0 0 10px;
  flex: 1;
}

.action-panel .el-card__footer {
  padding: 0 0 5px 10px;
}
</style>
