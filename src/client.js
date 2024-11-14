/* 通用客户端 */
import axios from 'axios'
import { getActiveLanguage } from '@/locale/index.js'
import store from '@/storage/index.js'

const config = store.getters.config

/* 构建userClient对象 */
const useClient = () => {
  let axiosInstance = axios.create({
    validateStatus: status => status >= 200 && status < 500, // 禁用异常抛出
    baseURL: config['API_ENDPOINT'],
    timeout: 10000,
  })

  // 拦截器配置，发送支持语言信息
  axiosInstance.interceptors.request.use((config) => {
    config.withCredentials = true  // 允许携带关键凭证
    config.headers['Accept-Language'] = getActiveLanguage()  // 携带语言头响应本地化
    return config
  }, (error) => {
    return Promise.reject(error);
  });

  return axiosInstance;
}

export { useClient }



















