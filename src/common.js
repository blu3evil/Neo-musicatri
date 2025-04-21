// 服务端响应类
export class Result {
  constructor(code, message = null, data = null) {
    this.code = code
    this.message = message
    this.data = data
  }

  static fromJSON(json) {
    return new Result(json.code, json.message, json.data)
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

  // 6xx前端错误，主要是建立连接时出错，例如超时或无法建立连接
  // 601: ERR_NETWORK: 网络错误
  // 602: ECONNABORTED: 连接错误
  isConnectionError() {
    return this.code === 601 || this.code === 602
  }
}


