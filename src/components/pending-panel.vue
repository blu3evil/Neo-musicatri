<!-- 授权结果信息回显 -->
<script>
import { getCurrentInstance } from 'vue'
import { useI18n } from 'vue-i18n'

export default {
  setup() {
    const instance = getCurrentInstance()
    const config = instance.appContext.config.globalProperties.$config
    const {t, locale} = useI18n()  // 本地化

    return {
      t
    }
  }
}
</script>

<template>
  <el-row class="row-bg full-height" align="middle" justify="center">
    <el-col :span="9">
      <el-card id="redirect-card" class="unselectable">  <!-- 设置背景色 -->
        <template #header>
          <div class="card-header">
            <slot></slot>
          </div>
        </template>
        <template #footer>{{t('component.pending-panel.footer')}}</template>
      </el-card>
    </el-col>
  </el-row>
</template>

<style scoped>
/* 高度置中 */
.full-height {
  height: 85vh;
}

#redirect-card {
  background-color: var(--redirect-card-bg-color);  /* 背景色 */
  --el-card-border-color: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.7);  /* 阴影效果 */
  backdrop-filter:blur(12px);  /* 添加模糊效果 */
  border: 1px;
  border-radius: 13px;
  color: var(--text-color);  /* 使用主题字色 */
  overflow: hidden;
  transition: var(--el-transition-duration)
}

/* discord oauth2认证重定向 */
#discord-oauth2-redirect-link {
  color: var(--a-color);
  transition: color 0.3s ease-in-out;
}


/* bad idea */
#discord-oauth2-redirect-link:hover {
  /*transform: translateY(-20px);*/     /* 向上浮动 5px */
  /*box-shadow: 0 4px 8px rgba(0, 0, 0, 0.80);*/  /* 增加阴影 */
  /*color: var(--a-color-2);*/
}

</style>
