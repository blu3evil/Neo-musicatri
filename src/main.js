// css主题初始化
import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
const app = createApp(App);

// vuex配置
import { store } from './storage'
app.use(store)

// axios初始化
import { config } from '@/config.js'
import { initClient } from '@/services/axios-client.js'
await initClient(config)

// i18n初始化
import { initI18n } from '@/locale/index.js'
app.use(initI18n(store.getters.activeLanguage))

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

// mitt事件初始化
import '@/mitt/listeners.js'

app.mount('#app')
