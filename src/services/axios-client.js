/* 通用客户端 */
import { getActiveLanguage } from '@/locale/index.js'
import store from '@/storage/index.js'
import axios from 'axios'

await store.dispatch('loadConfig')  // 等待加载完成
console.log(store.getters['config']['API_ENDPOINT'])
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

// 服务端响应类
class MusicatriResult {
  constructor(code, message, data) {
    this.code = code
    this.message = message
    this.data = data
  }

  // 是否成功
  isSuccess() {
    return this.code === 200
  }

  // 是否为客户端错误
  isClientError() {
    return this.code >= 400 && this.code < 500
  }

  // 是否为服务端错误
  isServerError() {
    return this.code >= 500 && this.code < 600
  }

  // 是否为连接错误
  isConnectionError() {
    return this.code === 601 || this.code === 602
  }
}

// 将响应封装为统一对象
client.interceptors.response.use(
  response => {
    // 服务端异常处理，统一响应形式
    return Promise.resolve(
      new MusicatriResult(
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
    return Promise.resolve(new MusicatriResult(code, message, error))
  }
)


/* 构建userClient对象 */
const useClient = () => client;
export { useClient }





















