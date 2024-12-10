/* 通用客户端 */
import axios from 'axios'
import { store } from '@/storage/index.js'
import { Result } from '@/common.js'

export let discordClient = null  // discord客户端
export let musicatriClient = null  // musicatri客户端


const musicatriClientResponseHandler = (response) => {
  return Promise.resolve(
    new Result(response.status, response.data.message, response.data.data)
  )
}

// axios异常处理器
const axiosErrorHandler = (error) => {
  let code = 600
  let message = error.message  || error

  if (error.code === 'ERR_NETWORK') code = 601  // 网络错误
  else if (error.code === 'ECONNABORTED') code = 602  // 连接错误

  // 避免抛出异常
  return Promise.resolve(new Result(code, message, error))
}

export const initClient = config => {
  // 初始化MusicatriAPI客户端
  const musicatriClientPrototype = axios.create({
    validateStatus: status => status >= 200 && status < 600, // 禁用异常抛出
    baseURL: config['API_ENDPOINT'] || 'http://localhost:5000/api/v1',
    timeout: config['REQUEST_TIMEOUT'] || 10000,
  })

  musicatriClientPrototype.interceptors.request.use((config) => {
    config.withCredentials = true  // 允许携带关键凭证
    config.headers['Accept-Language'] = store.getters.activeLanguage  // 携带语言头响应本地化
    return config
  }, (error) => {
    return Promise.reject(error);
  });

  // 将响应封装为统一对象
  musicatriClientPrototype.interceptors.response.use(
    musicatriClientResponseHandler,
    axiosErrorHandler
  )
  musicatriClient = musicatriClientPrototype


  // 初始化DiscordAPI客户端
  discordClient = axios.create({
    timeout: config['REQUEST_TIMEOUT'] || 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  discordClient.interceptors.response.use((
    response) => response,
    axiosErrorHandler)
}

















