// 认证服务
// noinspection JSUnresolvedReference

import { useClient } from '@/services/axios-client.js'
const client = useClient()  // 客户端

const urlPrefix = '/auth'

// 获取认证路径
export const getAuthorizeUrl = () =>
  client.get(`${urlPrefix}/authorize-url`)

// 用户登入
export const userLogin = () =>
  client.get(`${urlPrefix}/login`)

// 获取用户登入状态
export const getUserLoginStatus = () =>
  client.get(`${urlPrefix}/status`)

// 用户授权
export const userAuthorize = code =>
  client.post(`${urlPrefix}/authorize`, { code: code })


