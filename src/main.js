// css主题初始化
import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
const app = createApp(App);

// vuex配置
import store from './storage'
app.use(store)

import { i18n } from '@/locale/index.js'
app.use(i18n)  // 本地化

// 路由初始化
import { router } from './router.js'
app.use(router)

// element-plus初始化
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
app.use(ElementPlus)

// element-plus图表注册
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
