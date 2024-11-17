<!-- 授权结果信息回显 -->
<script>
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { computed, onMounted, onUnmounted, ref } from 'vue'

export default {
  setup(props, { expose }) {
    const store = useStore() // 存储
    const { t } = useI18n() // 本地化

    const links = ref([]) // 所有可用连接
    const title = ref('') // 标题
    const subtitle = ref('') // 子标题
    const ellipsis = ref('.') // 字符串加载动画
    const ellipsisDisplay = ref(false) // 加载字符串显示

    const message = ref('') // 消息
    const isError = ref(false) // 是否为错误消息
    const config = computed(() => store.getters.config)

    let ellipsisIntervalId = 0 // 字符串循环事件id

    // 设置标题
    const setTitle = (_title, _enableEllipsis) => {
      title.value = _title
      ellipsisDisplay.value = _enableEllipsis
      if (_enableEllipsis) {
        ellipsis.value = '.'
      }
    }

    // 设置子标题
    const setSubtitle = _title => {
      subtitle.value = _title
    }

    // 设置消息，默认为成功消息，通过_errorMessage来将消息设置为错误消息
    const setMessage = (_message, _isError = false) => {
      message.value = _message
      isError.value = _isError
    }

    // 添加一条链接
    const addLink = linkItem => {
      links.value.push(linkItem)
    }

    // 添加一个发送issue的链接
    const addIssueLink = () => {
      addLink({
        desc: t('view.UserLogin.sending_issue'),
        href: config.value['ISSUE_LINK'],
        target: '_blank',
      })
    }

    // 清除标题，如果在状态中调用了这个方法应该在fadeout中调用同样的方法来清除
    const clearTitle = () => {
      title.value = ''
      subtitle.value = ''
      ellipsisDisplay.value = false
    }

    const clearLinks = () => {
      links.value = []
    }

    // 清除消息
    const clearMessage = () => {
      message.value = ''
    }

    onMounted(() => {
      // 设置字符串循环
      ellipsisIntervalId = setInterval(() => {
        ellipsis.value = ellipsis.value.length < 4 ? ellipsis.value + '.' : '.'
      }, 500)
    })

    onUnmounted(() => {
      clearInterval(ellipsisIntervalId) // 清除字符串循环
    })

    // 将方法暴露到外部
    expose({
      setTitle,
      setSubtitle,
      setMessage,
      addLink,
      addIssueLink,
      clearTitle,
      clearLinks,
      clearMessage,
    })

    return {
      t,
      title,
      subtitle, // 子标题
      ellipsis, // 省略号
      ellipsisDisplay,
      message,
      isError,
      links,
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
              <a
                :href="link['href']"
                :target="link['target']"
                v-if="link['click'] == null"
              >
                {{ link['desc'] }}
                <!-- 超链接 -->
              </a>
              <a
                :href="link['href']"
                :target="link['target']"
                v-if="link['click'] != null"
                @click.prevent="link['click']"
              >
                {{ link['desc'] }}
                <!-- 事件链接 -->
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

/* 设置超链接样式 */
a {
  text-decoration: none; /* 去掉默认的下划线 */
  //text-decoration-color: lightgray;
  //text-decoration-thickness: 1px;
  position: relative; /* 设置为相对定位以便定位伪元素 */
  display: inline-block; /* 让元素像块级元素一样行为，方便控制大小 */
}

a:after {
  content: ''; /* 伪元素不需要文本内容 */
  position: absolute; /* 定位到父元素的底部 */
  bottom: 7px; /* 让线条位于超链接的底部 */
  left: 0; /* 从左边开始 */
  width: 100%; /* 初始宽度为 0 */
  height: 2px; /* 设置线条的高度 */
  background-color: var(--a-color); /* 设置线条颜色 */
  transform: scaleX(0); /* 初始状态为缩放为0 */
  transform-origin: bottom left; /* 动画从右侧开始 */
  transition: transform 0.3s ease-in-out;
}

a:hover::after {
  transform: scaleX(1); /* 鼠标悬停时扩展宽度至 100% */
  transform-origin: bottom left; /* 动画从左侧开始 */
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
