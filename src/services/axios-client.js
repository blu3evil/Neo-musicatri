/* 通用客户端 */
import { getActiveLanguage } from '@/locale/index.js'
import { ErrorTypes } from '@/services/error-types.js'
import store from '@/storage/index.js'
import axios from 'axios'

await store.dispatch('loadConfig')  // 等待加载完成
console.log(store.getters['config']['API_ENDPOINT'])
const config = store.getters.config

const client = axios.create({
  validateStatus: status => status >= 200 && status < 500, // 禁用异常抛出
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

client.interceptors.response.use(response => {
  // 服务端异常处理，统一响应形式
  let message = response.data.message
  let data = response.data
  let status = response.status
  if (status === 200) {
    // 请求成功
    return { success: true, message: message, data: data }
  } else if (status >= 400 && status < 500) {
    // 客户端错误
    if (status === 401) return { success: false, message: message, errorType: ErrorTypes.UNAUTHORIZED }
    if (status === 403) return { success: false, message: message, errorType: ErrorTypes.FORBIDDEN }
    if (status === 404) return { success: false, message: message, errorType: ErrorTypes.NOTFOUND }
    return { success: false, message: message, data: data, errorType: ErrorTypes.CLIENT_ERROR }
  } else if (status >= 500 && status < 600) {
    // 服务端异常
    return { success: false, message: message, data: data, errorType: ErrorTypes.SERVER_ERROR }
  } else {
    // 未知异常
    return { success: false, message: message, data: data, errorType: ErrorTypes.UNAUTHORIZED }
  }
},

  // axios异常处理
error => {
  if (error.code === 'ERR_NETWORK' || error.code === 'ECONNABORTED') {
    // 服务器链接异常
    return { success: false, message: error, errorType: ErrorTypes.CONNECTION_ERROR }
  } else {
    // 未知异常
    return { success: false, message: error, errorType: ErrorTypes.UNKNOWN_ERROR }
  }
})


/* 构建userClient对象 */
const useClient = () => client;
export { useClient }





















