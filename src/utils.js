// 状态模式
// 健康检查
class AbstractState {
  // 切入状态时被调用
  enter(context) {
    // 状态执行逻辑
  }

  // 切出状态时被调用
  fadeout(context) {
    // 退出状态逻辑
  }
}

class StateContext {
  constructor () {
    this.state = null
  }

  setState (state) {
    if (this.state !== null) this.state.fadeout(this)  // 状态退出
    this.state = state  // 切换状态
    if (this.state !== null) this.state.enter(this)  // 切入状态
  }
}

export {
  AbstractState,
  StateContext,
}

// 服务端响应类
export class MusicatriResult {
  constructor(code, message=null, data=null) {
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
