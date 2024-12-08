<!-- 授权结果信息回显 -->
<script>
import { useI18n } from 'vue-i18n'
import { onMounted, onUnmounted, ref } from 'vue'

export default {
  setup(props, { expose }) {
    const { t } = useI18n() // 本地化
    const panelTitle = ref('') // 标题

    const panelEllipsisDisplay = ref(false) // 加载字符串显示
    const panelEllipsis = ref('.') // 字符串加载动画
    const panelSubtitle = ref('') // 子标题
    let panelEllipsisIntervalId = 0 // 字符串循环事件id

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
      if (ellipsisDisplay) {
        panelEllipsis.value = '.'
      }
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

    /**
     * 添加事件链接
     */
    const appendEventLink = (name, event) => {
      panelLinks.value.push({
        desc: name,
        href: '/',
        target: null,
        click: event
      })
    }

    /**
     * 添加跳转链接
     */
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

    onMounted(() => {
      // 设置字符串循环
      panelEllipsisIntervalId = setInterval(() => {
        panelEllipsis.value = panelEllipsis.value.length < 4 ? panelEllipsis.value + '.' : '.'
      }, 500)
    })

    onUnmounted(() => {
      clearInterval(panelEllipsisIntervalId) // 清除字符串循环
    })

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
      ellipsis: panelEllipsis, // 省略号
      ellipsisDisplay: panelEllipsisDisplay,
      message: panelMessage,
      isError: isErrorMessage,
      links: panelLinks,
    }
  },
}
</script>

<template>
  <el-row class="row-bg full-height" align="middle" justify="center">
    <el-col :style="{ display: 'flex', alignItems: 'center', justifyContent: 'center' }">
      <el-card id="redirect-card" style="width: 800px" class="unselectable">
        <!-- 设置背景色 -->
        <template #header>
          <div class="card-header">
            <h2>
              <span>{{ title }}</span>
              <span v-if="ellipsisDisplay">{{ ellipsis }}</span>
            </h2>
            {{ subtitle }}
            <h3 class="text-error" v-if="isError">{{ message }}</h3>
            <h3 class="text-success" v-if="!isError">{{ message }}</h3>
            <div v-for="link in links">
              <a class="slide-animation-a"
                :href="link['href']"
                :target="link['target']"
                v-if="link['click'] == null"
              >
                <!-- 超链接 -->
                {{ link['desc'] }}
              </a>
              <a class="slide-animation-a"
                :href="link['href']"
                :target="link['target']"
                v-if="link['click'] != null"
                @click.prevent="link['click']"
              >
                <!-- 事件链接 -->
                {{ link['desc'] }}
              </a>
            </div>
          </div>
        </template>
        <template #footer>{{ t('component.pending-panel.footer') }}</template>
      </el-card>
    </el-col>
  </el-row>
</template>

<style scoped>
/* 高度置中 */
.full-height {
  height: 85vh;
}

#redirect-card {
  background-color: var(--redirect-card-bg-color); /* 背景色 */
  --el-card-border-color: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.7); /* 阴影效果 */
  backdrop-filter: blur(12px); /* 添加模糊效果 */
  border: 1px;
  border-radius: 13px;
  color: var(--text-color); /* 使用主题字色 */
  overflow: hidden;
  transition: var(--el-transition-duration);
}
</style>
