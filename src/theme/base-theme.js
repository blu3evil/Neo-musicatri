/**
 * 基础主题，即亮色主题，关于主题的定义可以参考此对象的定义，
 * 通过覆盖的形式避免一些css样式表遗漏
 */
const baseStyle = {
  '--bg-color': '#f5f0f0',
  '--bg-color-2': '#c9c9c9',
  '--divider-color': '#2c3e50',  /* 分割线 */

  '--text-color': '#2c3e50',
  '--error-color': '#ff0000' /* 错误消息颜色 */,
  '--success-color': '#797826' /* 成功消息颜色 */,

  '--a-color': '#344dc5',
  '--a-color-2': '#3047b4',

  '--popper-bg-color': '#ffffff',  /* 弹出框颜色 */
  '--popper-hover-bg-color': '#e5e5e5',  /* 弹出框悬浮背景色 */
  '--popper-border-color': '#27ceb9',  /* 弹出框边框颜色 */

  '--navbar-color': '#2c3e50',
  '--navbar-bg-color': '#c9c9c9',
  '--redirect-card-bg-color': 'rgba(201, 201, 201, 1.0)',
}

export { baseStyle }