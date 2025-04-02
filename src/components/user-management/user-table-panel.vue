<!-- 用户管理列表 -->
<script>
import CommonPanel from '@/components/common-panel.vue'
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { userService } from '@/services/user-service.js'
import { globalEventbus } from '@/mitt/global-eventbus.js'
import { Events } from '@/events.js'

export default {
  components: { CommonPanel },
  setup() {
    const { t } = useI18n()
    const formInline = reactive({
      username: '',
      global_name: '',
      is_active: -1,
    })

    // 表格标签
    const usernameLabel = computed(() => t("view.workspace.UserManagement.username_label"))
    const globalNameLabel = computed(() => t("view.workspace.UserManagement.global_name_label"))
    const rolesLabel = computed(() => t("view.workspace.UserManagement.roles_label"))
    const isActiveLabel = computed(() => t("view.workspace.UserManagement.is_active_label"))
    const fuzzyQueryPlaceholder = computed(() => t("view.workspace.UserManagement.fuzzy_query_placeholder"))
    const activeStatus = computed(() => t("global.active"))
    const bannedStatus = computed(() => t("global.banned"))
    const anyStatus = computed(() => t('global.any'))
    const emptyText = computed(() => t("view.workspace.UserManagement.empty_text"))
    const isLoading = ref(true)

    const tableData = ref([])

    // 格式化权限信息
    function formatRoles(roles) {
      if (!roles) return [t('global.traveler')];
      const roleMap = {
        admin: t('global.admin'),
        user: t('global.user')
      };
      return roles.map(role => roleMap[role]).filter(Boolean);
    }

    function formatIsActive(isActive) {
      return isActive ? t('global.active') : t('global.banned');
    }

    // todo: 按内容自定义列字符串颜色
    const getIsActiveClassName = (row) => {
      return row.is_active_class_name ? 'text-success' : 'text-error'
    }

    // 格式化后端数据
    // noinspection JSUnresolvedReference
    const formattedTableData = computed(() => tableData.value.map(userData => ({
      id: userData.id,
      username: userData.username,
      global_name: userData.global_name,
      roles: formatRoles(userData.roles),
      is_active: formatIsActive(userData.is_active),
      is_active_class_name: userData.is_active,
    })))

    // 处理某一行被点击，查询某个用户的详细信息
    const handleRowClick = (row, column, event) => {
      console.log(row.id)
    }

    // 刷新用户表格
    async function refreshUserTable() {
      isLoading.value = true
      const result = await userService.getUsersPreview()  // 加载用户数据概览
      if (result.isSuccess()) {
        // 成功获取用户概览数据
        tableData.value = result.data
        globalEventbus.emit(Events.MITT.USER_MANAGEMENT.LOAD_USERS_PREVIEW.LOAD_SUCCESS)
      } else {
        // 获取用户数据概览失败，使用mitt触发事件
        globalEventbus.emit(Events.MITT.USER_MANAGEMENT.LOAD_USERS_PREVIEW.LOAD_FAILED, result.message)
      }
      isLoading.value = false
    }

    const onSubmit = () => {
      console.log('submit!')
    }

    onMounted(() => {
      refreshUserTable()  // 加载完成时刷新表格
    })

    return {
      t,
      formattedTableData,  // 经过格式化的表单数据
      formInline,
      usernameLabel,
      globalNameLabel,
      rolesLabel,
      isActiveLabel,
      fuzzyQueryPlaceholder,  // 模糊查询表单占位符
      anyStatus,
      activeStatus,
      bannedStatus,
      emptyText,
      isLoading,
      onSubmit,
      getIsActiveClassName,
      handleRowClick,  // 查询某个用户详情
    }
  }
}
</script>
<template>
<!-- 用户检索表单 -->
    <CommonPanel style="height: 55px;">
      <el-form :inline="true" :model="formInline" class="user-table-search">
        <el-form-item :label="globalNameLabel">
          <el-input v-model="formInline.global_name"
                    :placeholder="fuzzyQueryPlaceholder"
                    clearable
                    class="text-mini"
                    style="width: 200px"
          />
        </el-form-item>
        <el-form-item :label="usernameLabel">
          <el-input v-model="formInline.username"
                    :placeholder="fuzzyQueryPlaceholder"
                    clearable
                    class="text-mini"
                    style="width: 200px"
          />
        </el-form-item>
        <el-form-item :label="isActiveLabel">
          <el-select v-model="formInline.is_active" style="width: 130px">
            <el-option :label="anyStatus" :value="-1" />
            <el-option :label="bannedStatus" :value="0" />
            <el-option :label="activeStatus" :value="1" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSubmit"
                     style="font-size: var(--text-small)">
            {{t("view.workspace.UserManagement.query")}}
          </el-button>
        </el-form-item>
      </el-form>
    </CommonPanel>

<!-- 用户表格 -->
    <CommonPanel style="height: 600px;" v-loading="isLoading">
      <el-table :data="formattedTableData"
                max-height="500"
                @row-click="handleRowClick"
                :empty-text="emptyText"
      >
        <el-table-column type="index" width="50" />
        <el-table-column prop="username" :label="usernameLabel" width="180" />
        <el-table-column prop="global_name" :label="globalNameLabel" width="180" />
        <el-table-column prop="roles" :label="rolesLabel" width="180" />
        <el-table-column prop="is_active" :label="isActiveLabel" />
      </el-table>
    </CommonPanel>
</template>
<style scoped>
.el-card {
  width: auto;
  margin-top: 10px
}

</style>


<style>
.user-table-search {
  margin-left: 10px
}

.user-table-search .el-input {
  --el-input-width: 150px;
  --el-input-bg-color: var(--bg-color);
  --el-input-border-color: var(--popper-border-color);
  --el-input-focus-border-color: var(--popper-border-color);
  --el-input-hover-border-color: var(--popper-border-color);
  --el-input-clear-hover-color: var(--popper-border-color);
  font-size: var(--text-small)
}

.el-input__inner {
  color: var(--text-color);
  font-family: inherit;
}

.user-table-search .el-select {
  --el-select-width: 220px;
}

.el-card__header {
  padding: 10px 0 0 10px;
}

.el-form-item__label {
  font-size: var(--text-small);
  color: var(--text-color);
}

.el-card__body {
  padding: 0 0 0 0;
  flex: 1;
}

.el-card__footer {
  padding: 0 0 5px 10px;
}

.el-table__empty-block {
  background-color: var(--bg-color-2);
  font-size: var(--text-medium);
}

.el-table {
  --el-table-tr-bg-color: var(--bg-color-2);  /* 行背景色 */
  --el-table-border-color: var(--bg-color-2);  /* 行边界颜色 */
  --el-table-header-bg-color: var(--bg-color-2);  /* 表头背景色 */
  --el-table-header-text-color: var(--text-color);
  --el-scrollbar-hover-bg-color: var(--bg-color-2);  /* 拖动条悬停背景色 */
  --el-table-row-hover-bg-color: var(--bg-color);  /* 行悬停背景色 */
  color: var(--text-color);
  font-size: var(--text-small);
}

.el-loading-mask {
  background-color: var(--bg-color-2);
  transition: none;
  --el-color-primary: var(--text-color);
}


</style>
