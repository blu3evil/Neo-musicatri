/**
 * 前端和后端使用同一套响应码
 */
export const HttpCode = {
  SUCCESS: 20000,  // 操作成功

  // CLIENT级别错误
  CLIENT_ERROR: 40000,  // 客户端错误
  NOT_FOUND: 40400,  // 资源未找到
  INVALID_REQUEST_PARAMS: 40001,  // 请求参数无效
  AUTHENTICATION_FAILED: 40002,   // 认证失败
  PERMISSION_DENIED: 40003,  // 权限不足
  TOKEN_EXPIRED: 40004,  // token过期
  TOKEN_INVALID: 40005,  // token无效
  TOKEN_SESSION_INACTIVE: 40006,  // jwt会话已经被关闭

  // SERVER级别错误
  INTERNAL_SERVER_ERROR: 50000,  // 服务器内部错误
  NETWORK_ERROR: 50001,  // 网络错误

  // axios错误
  AXIOS_NETWORK_ERROR: 60000,  // axios网络错误，通常是无法建立到后端的连接
  SERVER_TIMEOUT: 60001,  // 服务端响应超时

}
