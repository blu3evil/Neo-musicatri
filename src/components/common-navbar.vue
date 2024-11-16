<script>
import { computed, getCurrentInstance, onMounted, ref } from 'vue'
import { setTheme, getThemes, getActiveThemeId } from '@/theme'
import { useRouter } from 'vue-router'
import { availableLanguages, getActiveLanguage, getLanguageDisplayName } from '@/locale/index.js'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import { useNavigateHelper } from '@/router.js'

export default {
  setup() {
    const activeIndex = ref('1')  // 菜单栏当前激活
    const handleSelect = (key, keyPath) => {
      // console.log(key, keyPath)
    }

    const router = useRouter()  // 路由
    const store = useStore()  // 存储
    const navigateHelper = useNavigateHelper()

    const instance = getCurrentInstance() // 获取当前实例
    const config = instance.appContext.config.globalProperties.$config  // 配置
    const activeSettingPage = computed(() => store.getters.activeSettingPage)

    const { t ,locale } = useI18n()  // 本地化
    const activeLanguage = ref('')
    const activeThemeId = ref('')
    const hoverIndex = ref({})  // 当前鼠标悬停索引，用于着重染色
    const themes = computed(() => getThemes())  // 主题列表
    const popperStyle = ref('top: 70px')  // 弹出框统一样式

    /**
     * 设置当前语言
     * @param lang 目标语言
     */
    const onLangOptionClick = (lang) => {
      if (activeLanguage === lang)  return         // 语言相同
      if (availableLanguages.indexOf(lang) === -1)  return   // 语言不支持
      localStorage.setItem('locale', lang);  // 在localstorage设置语言
      activeLanguage.value = lang  // 当前语言
      locale.value = lang; // 切换语言，更新响应式
    }

    /**
     * 设置当前主题
     * @param themeId 目标主题Id
     */
    const onThemeOptionClick = (themeId) => {
      setTheme(themeId)
      activeThemeId.value = getActiveThemeId()
    }

    /**
     * 进入项目设置页面
     */
    const onAppSettingClick = () => {
      let currentPath = router.currentRoute.value.path
      if (!currentPath.startsWith('/settings')) {
        // 当前路径不以/settings开头，记录下这个路径，并在将来回溯
        store.commit('setPathBeforeIntoSettingPage', currentPath)
        router.push(`/settings/${activeSettingPage.value}`)
      } else {
        // 当前路径以/settings开头，那么回到原来进入设置页面之前的路径
        let before = store.getters.pathBeforeIntoSettingPage
        if (before != null && before !== '') {
          router.push(before)  // 如果before路径存在
        } else {
          navigateHelper.toIndex()  // 否则跳转到主页
        }
      }
    }

    onMounted(() => {
      activeThemeId.value = getActiveThemeId()
      activeLanguage.value = getActiveLanguage()        // 设置当前语言id
    })

    // github链接
    const onGithubLinkClick = () => {
      const githubLink = config['GITHUB_LINK']
      window.open(githubLink, '_blank') // 在新标签页中打开链接
    }

    // discord链接
    const onDiscordLinkClick = () => {
      const discordLink = config['DISCORD_LINK'] // 替换为个人资料页面的 URL
      window.open(discordLink, '_blank') // 在新标签页中打开链接
    }

    // logo链接，跳转到登录页/user/login
    const onNavbarLogoClick = () => {
      navigateHelper.toUserIndex()
    }

    return {
      activeIndex,
      activeSettingPage,  // 当前激活页面
      hoverIndex,

      handleSelect, //
      onNavbarLogoClick, // logo被点击
      onGithubLinkClick, // github链接被点击
      onDiscordLinkClick, // discord链接被点击
      onAppSettingClick, // 项目设置页面
      popperStyle,  // 弹出框统一样式1

      availableLanguages,
      onLangOptionClick,
      activeLanguage,
      getLanguageDisplayName,   // 获取语言显示名称

      themes,
      activeThemeId,  // 当前主题
      onThemeOptionClick,  // 选择主题
      getCurrentThemeName: getActiveThemeId,

      t  // 本地化
    }
  },
}
</script>

<template>
  <el-menu
    :default-active="activeIndex"
    class="user-navbar"
    mode="horizontal"
    :ellipsis="false"
    @select="handleSelect"
  >
    <!-- logo -->
    <el-menu-item index="0" @click="onNavbarLogoClick">
      <img
        style="width: 150px; margin-bottom: 2px"
        src="/src/assets/common-navbar/navbar-logo.png"
        alt="Element logo"
      />
      <h1 id="navbar-title" style="margin-top: 6px">Musicatri</h1>
    </el-menu-item>

    <!-- 主题选择 -->
    <el-menu-item index="1">
      <el-popover
        popper-class="navbar-popper"
        :popper-style="popperStyle"
      >
        <template #reference>
          <img src="/src/assets/common-navbar/icon-theme.png"
               style="height: 46px"
               @click="onThemeOptionClick"
               alt="theme logo"/>
        </template>
        <template #default>
          <div v-for="(theme, index) in themes">
            <div :key="index"
                 class="lang-select-item"
                 @mouseover="hoverIndex.value = index"
                 @mouseleave="hoverIndex.value = null"
                 :style="{
                  backgroundColor: hoverIndex.value === index ? 'var(--popper-hover-bg-color)' : 'transparent',
                  width: '100%',
                  textIndent: '20px'  // 文本偏移
                }"
                 @click="onThemeOptionClick(theme['id'])"
            >
              <span v-if="activeThemeId === theme['id']">> {{theme['name']}}</span>
              <span v-else>- {{theme['name']}}</span>
            </div>
          </div>

        </template>
      </el-popover>
    </el-menu-item>

    <!-- discord跳转链接 -->
    <el-menu-item index="1">
      <el-popover
        placement="top-start"
        :width="320"
        trigger="hover"
        popper-class="navbar-popper"
        :popper-style="popperStyle"
        :content="t('component.common-navbar.discord_logo')"
      >
        <template #reference>
          <img src="/src/assets/common-navbar/icon-discord.png"
               style="height: 36px"
               @click="onDiscordLinkClick"
               alt="discord logo"/>
        </template>
      </el-popover>
    </el-menu-item>

    <!-- github跳转链接 -->
    <el-menu-item index="2">
      <el-popover
        placement="top-start"
        :width="310"
        trigger="hover"
        popper-class="navbar-popper"
        :popper-style="popperStyle"
        :content="t('component.common-navbar.github_logo')"
      >
        <template #reference>
          <img src="/src/assets/common-navbar/icon-github.png"
               style="height: 39px"
               @click="onGithubLinkClick"
               alt="github logo"/>
        </template>
      </el-popover>
    </el-menu-item>

    <!-- 项目设置 -->
    <el-menu-item index="2">

      <el-popover
        placement="top-start"
        :width="240"
        trigger="hover"
        popper-class="navbar-popper"
        :popper-style="popperStyle"
        :content="t('component.common-navbar.setting_logo')"
      >
        <template #reference>
          <img src="/src/assets/common-navbar/icon-setting.png"
               style="height: 39px"
               @click="onAppSettingClick"
               alt="setting logo"/>
        </template>
      </el-popover>
    </el-menu-item>
  </el-menu>
</template>

<style scoped>
/* 菜单栏按钮右对齐 */
.el-menu--horizontal > .el-menu-item:nth-child(1) {
  margin-right: auto;
}

/* 菜单栏按钮悬停 */
.el-menu--horizontal .el-menu-item:not(.is-disabled):focus,
.el-menu--horizontal .el-menu-item:not(.is-disabled):hover {
  background-color: transparent; /* 隐藏按钮悬停背景色 */
  color: var(--el-menu-hover-text-color);
  outline: none;
}

/* 菜单栏按钮激活时 */
.el-menu--horizontal > .el-menu-item.is-active {
  border-bottom: none;
  border-bottom: transparent; /* 隐藏底边色 */
  color: #4b5c6e !important;
}

/* 导航栏 */
.el-menu {
  /*background-color: transparent;*/ /* 隐藏导航栏背景色 */
  background: var(--navbar-bg-color);
  /*backdrop-filter: blur(10px);*/ /* 添加模糊效果 */
  border: none; /* 隐藏导航栏底边 */
  height: 75px;
}

/* 菜单栏按钮取消底栏 */
.el-menu--horizontal > .el-menu-item {
  border: none;
  height: 100%;
  margin: 0;
}

/* 图标 */
.el-avatar {
  --el-avatar-bg-color: transparent; /* 设置github图标背景色 */
}

/* 导航栏标题 */
#navbar-title {
  font-size: var(--text-large);
  font-weight: bold;
}

/* 导航栏标题字色 */
.el-menu--horizontal > .el-menu-item {
  color: var(--navbar-color);
}

/* 阻止默认hover效果 */
.el-menu-item:hover {
  background-color: transparent !important; /* 设置为透明或您想要的颜色 */
  color: inherit !important; /* 保持文本颜色 */
}

.el-menu-item {
  user-select: none;
  -webkit-user-select: none; /* Safari */
  -moz-user-select: none;    /* Firefox */
  -ms-user-select: none;     /* Internet Explorer/Edge */
}

/* 导航栏标题激活时字色 */
.el-menu--horizontal > .el-menu-item.is-active {
  border-bottom: transparent;
  color: var(--navbar-color) !important;
}

.lang-select-item:hover {

}
</style>
