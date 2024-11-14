// css主题初始化
import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
const app = createApp(App);

// vuex配置
import store from './storage'
app.use(store)

import { initI18n } from '@/locale/index.js'
app.use(initI18n())  // 本地化

// 路由初始化
import router from './router.js'
app.use(router)

// 事件总线初始化
import mitt from 'mitt'
app.config.globalProperties.$eventBus = mitt()

// 初始化配置、axios
import axios from 'axios'
app.config.globalProperties.$axios = axios
function getServerConfig () {  // 读取配置文件资源
  return new Promise ((resolve, reject) => {
    // public目录下的资源可以直接使用"/"访问
    axios.get('/config.json').then(data => {
      // console.log(data.data)
      // 绑定config对象到全局
      app.config.globalProperties.$config = data.data;
      // console.log(app.config.globalProperties.$config)
      resolve();
    }).catch(error => {
      console.log(error);
      reject()
    })
  })
}
async function init() {  // 异步调用初始化方法
  await getServerConfig();
}
app.use(init);  // 执行初始化

// element-plus初始化
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
app.use(ElementPlus)

// element-plus图表注册
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 初始化主题
import { initTheme } from '@/theme'
initTheme()

app.mount('#app')
