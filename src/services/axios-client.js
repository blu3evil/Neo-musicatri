/* 通用客户端 */
import { getActiveLanguage } from '@/locale/index.js'
import axios from 'axios'


import { store } from '@/storage/index.js'
import { Result } from '@/common.js'
await store.dispatch('loadConfig')  // 加载配置
const config = store.getters.config

const client = axios.create({
  validateStatus: status => status >= 200 && status < 600, // 禁用异常抛出
  baseURL: config['API_ENDPOINT'],
  timeout: 10000,
})

client.interceptors.request.use((config) => {
  config.withCredentials = true  // 允许携带关键凭证
  config.headers['Accept-Language'] = getActiveLanguage()  // 携带语言头响应本地化
  return config
}, (error) => {
  return Promise.reject(error);
});

// 将响应封装为统一对象
client.interceptors.response.use(
  response => {
    // 服务端异常处理，统一响应形式
    return Promise.resolve(
      new Result(
        response.status, response.data.message, response.data.data
      )
    )
  },
  // axios异常处理，统一相应格式
  error => {
    let code = 600
    let message = error.message  || error

    if (error.code === 'ERR_NETWORK') code = 601  // 网络错误
    else if (error.code === 'ECONNABORTED') code = 602  // 连接错误

    // 避免抛出异常
    return Promise.resolve(new Result(code, message, error))
  }
)

/* 构建userClient对象 */
const useClient = () => client;
export { useClient }





















