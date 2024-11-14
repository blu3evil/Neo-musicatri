// 认证服务
// noinspection JSUnresolvedReference

import { useClient } from '@/services/axios-client.js'

const client = useClient()  // 客户端

// 获取认证路径
const getAuthorizeUrl = async () => {
  return await client.get('/auth/authorize-url')
}

// 获取用户登入状态
const getUserLoginStatus = async () => {
  return await client.get('/auth/status')
}

// 用户登入
const userLogin = async () => {
  return await client.get('/auth/login')
}

// 用户授权
const userAuthorize = async (code) => {
  return await client.post('/auth/authorize', { code: code })
}

export {
  userLogin,
  userAuthorize,
  getAuthorizeUrl,
  getUserLoginStatus
}


