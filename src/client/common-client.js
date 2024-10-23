/* 通用客户端 */
import axios from 'axios'
import store from '@/storage/index.js'  // 存储

import { getCurrentInstance } from 'vue'
import { getActiveLanguage } from '@/locale/index.js'

const nulls = [null, 'null', '']

/* 构建userClient对象 */
const createCommonClient = () => {
  const instance = getCurrentInstance();
  if (!instance) {
    throw new Error('createUserClient must be called within a setup function.');
  }

  let axiosInstance = axios.create({
    baseURL: instance.appContext.config.globalProperties.$config['API_ENDPOINT'],
    timeout: 10000,
  })

  // 拦截器配置，发送支持语言信息
  axiosInstance.interceptors.request.use((config) => {
    // 设置 Accept-Language 请求头
    config.headers['Accept-Language'] = getActiveLanguage()

    if (store.getters != null) {
      // 通过vuex获取认证信息，在认证信息不为空的时候携带在请求头当中
      let accessToken = store.getters.accessToken  // accessToken授权凭据
      if (!nulls.includes(accessToken)) {
        config.headers['Authorization'] = accessToken
      }

      let deviceId = store.getters.deviceId  // deviceId设备id
      if (!nulls.includes(deviceId)) {
        config.headers['Device-ID'] = deviceId
      }
    }

    return config
  }, (error) => {
    return Promise.reject(error);
  });

  return axiosInstance;
}

export { createCommonClient }



















