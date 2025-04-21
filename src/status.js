// 头像状态
export const AvatarStatus = Object.freeze({
  IDLE: 'idle',  /* 头像未准备时 */
  LOADING: 'loading',  /* 头像正在加载 */
  PREPARED: 'prepared',  /* 为状态嵌入avatar hash，头像已经就绪但未加载 */
  COMPLETED: 'completed',  /* 头像加载完成 */
  FAILED: 'failed',  /* 头像加载失败 */
})
