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
