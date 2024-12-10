// 状态模式
export class AbstractState {
  // 切入状态时被调用
  enter(context) {
    // 状态执行逻辑
  }
  // 切出状态时被调用
  fadeout(context) {
    // 退出状态逻辑
  }
  // 状态定位符
  getIdentify() {
    return "undefined"
  }
}

export class StateContext {
  constructor (state=null) {
    this.state = state
  }
  // 设置状态
  setState (state) {
    if (this.state !== null) this.state.fadeout(this)  // 状态退出
    this.state = state  // 切换状态
    if (this.state !== null) this.state.enter(this)  // 切入状态
  }
  // 获得当前状态
  getState () {
    return this.state
  }
}

