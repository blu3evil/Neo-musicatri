<!-- 用户管理列表 -->
<script>
import CommonPanel from '@/components/common-panel.vue'
import { computed, onMounted, reactive, ref, toRaw } from 'vue'
import { useI18n } from 'vue-i18n'
import { adminUserServiceV1 } from '@/services/admin/user-service.js'
import { globalEventbus } from '@/mitt/global-eventbus.js'
import { Events } from '@/events.js'
import UserAvatarV2 from '@/components/user-avatar-v2.vue'
import { useStore } from 'vuex'
import { PopupMessage } from '@/utils/ui-helper.js'

export default {
  components: { UserAvatarV2, CommonPanel },
  setup() {
    const { t } = useI18n()
    const userQueryForm = reactive({
      username: '',
      global_name: '',
      is_active: -1,
      currentPage: 1,
      pageSize: 10
    })

    const targetUserForm = reactive({
      accent_color: null,
      avatar: "",
      avatar_decoration_data: null,
      banner: null,
      banner_color: null,
      clan: null,
      discriminator: "0",
      flags: 0,
      global_name: "",
      id: "",
      is_active: 0,
      locale: "zh-CN",
      mfa_enable: false,
      premium_type: 0,
      public_flags: 0,
      roles: [],
      username: ""
    })

    const targetUserFormCache = reactive({})

    // 当前可用权限等级  todo: 修改为从后端接口获取
    const roleOptions = ref([
      {
        id: '0',
        name: 'admin',
        description: 'Admin role'
      }
    ])

    const currentPage = ref(1)
    const pageSize = ref(10)
    const paginationSize = ref('default')
    const paginationBackground = ref(false)
    const paginationDisable = ref(false)

    const store = useStore()
    const targetUserAvatarContext = computed(() => {
      let targetUserId = targetUserForm.id
      return store.getters.safeUserAvatarContexts(targetUserId)
    })  /* 当前查询用户头像信息上下文 */

    // 表格标签
    const usernameLabel = computed(() => t('view.workspace.UserManagement.username_label'))
    const globalNameLabel = computed(() => t('view.workspace.UserManagement.global_name_label'))
    const rolesLabel = computed(() => t('view.workspace.UserManagement.roles_label'))
    const isActiveLabel = computed(() => t('view.workspace.UserManagement.is_active_label'))
    const userIdLabel = computed(() => t('view.workspace.UserManagement.user_id'))
    const operationLabel = computed(() => t('view.workspace.UserManagement.operation_label'))

    const fuzzyQueryPlaceholder = computed(() => t('view.workspace.UserManagement.fuzzy_query_placeholder'))
    const activeStatus = computed(() => t('global.active'))
    const bannedStatus = computed(() => t('global.banned'))
    const anyStatus = computed(() => t('global.any'))
    const emptyText = computed(() =>
      t('view.workspace.UserManagement.empty_text'),
    )
    const isTableLoading = ref(true)  // 表格是否加载
    const isPanelLoading = ref(true)  // 用户面板是否加载

    const dialogVisible = ref(false) // 弹窗是否可见
    const tableData = ref([])
    const tableCount = ref(0)  // 记录总数

    // 格式化权限信息
    function formatRoles(roles) {
      if (!roles) return [t('global.traveler')]
      const roleMap = {
        admin: t('global.admin'),
        user: t('global.user'),
      }
      return roles.map(role => roleMap[role]).filter(Boolean)
    }

    function formatIsActive(isActive) {
      return isActive ? t('global.active') : t('global.banned')
    }

    // todo: 按内容自定义列字符串颜色
    const getIsActiveClassName = row => {
      return row.is_active_class_name ? 'text-success' : 'text-error'
    }

    // 格式化后端数据
    // noinspection JSUnresolvedReference
    const formattedTableData = computed(() =>
      tableData.value.map(userData => ({
        id: userData.id,
        username: userData.username,
        global_name: userData.global_name,
        roles: formatRoles(userData.roles),
        is_active: formatIsActive(userData.is_active),
        is_active_class_name: userData.is_active,
      })),
    )

    // 处理某一行被点击，查询某个用户的详细信息
    const handleRowClick = async (row, column, event) => {
      dialogVisible.value = true
      isPanelLoading.value = true

      // 加载用户详情信息 todo: 一些展示用户详情加载失败的信息
      let userId = row.id
      let result = await adminUserServiceV1.getUserDetails(userId)
      if (!result.isSuccess()) {
        // 请求用户详情失败
        return
      }

      Object.assign(targetUserForm, result.data)
      Object.assign(targetUserFormCache, result.data)  // 同时将用户数据添加到缓存当中

      // 加载可用权限级别
      result = await adminUserServiceV1.getAllRoles()
      if (!result.isSuccess()) {
        // 权限级别请求失败
        return
      }
      roleOptions.value = result.data

      // 加载头像
      // noinspection JSUnresolvedReference
      store.dispatch('prepareAvatar', {
        id: targetUserForm.id,
        avatar: targetUserForm.avatar,
      }).then()

      store.dispatch('loadAvatar', {
        id: targetUserForm.id
      }).then()

      isPanelLoading.value = false  // 加载完成
    }

    // 比较表单数据是否被修改
    function compareTargetUserForm(cache, current) {
      // 比较权限是否被修改
      if (cache.roles.length !== current.roles.length) return false

      const sortedCacheRoles = cache.roles.slice().sort()
      const sortedCurrentRoles = current.roles.slice().sort()

      sortedCacheRoles.every((val, index) => {
        if (val !== sortedCurrentRoles[index]) return false
      })

      // 比较状态是否被修改
      return cache.is_active === current.is_active;
    }

    // 处理用户删除
    const handleUserDelete = () => {
      let globalName = targetUserForm.global_name
      PopupMessage.warning(t('view.workspace.UserManagement.delete_user_or_not', {
        globalName,
      })).then(async () => {
        // 确认删除用户
        const result = await adminUserServiceV1.deleteUser(targetUserForm.id)
        if (result.isSuccess()) {
          // 删除成功
          globalEventbus.emit(Events.MITT.USER.DELETE.SUCCESS, {
            globalName
          })
          dialogVisible.value = false
          await refreshUserTable()  // 刷新表格
        } else {
          // 删除失败
          globalEventbus.emit(Events.MITT.USER.DELETE.FAILED, {
            globalName,
            reason: result.message
          })
        }
      }).catch(() => {
        // 取消删除用户
      })
    }

    // 当弹窗关闭时比较当前表单和缓存是否相同
    const handleDialogClose = () => {
      if (!compareTargetUserForm(targetUserFormCache, targetUserForm)) {
        // 缓存与原始值不同，弹窗询问是否提交修改
        let globalName = targetUserForm.global_name
        PopupMessage.warning(t('view.workspace.UserManagement.submit_change_or_not'))
          .then(async () => {

            // 提交patch请求修改用户数据
            const result = await adminUserServiceV1.patchUser(targetUserForm.id, {
              'is_active': targetUserForm.is_active,
              'roles': targetUserForm.roles
            })

            if (result.isSuccess()) {  // 修改成功
              globalEventbus.emit(Events.MITT.USER.DATA.PATCH.SUCCESS, globalName)
            } else {
              // 修改失败
              globalEventbus.emit(Events.MITT.USER.DATA.PATCH.FAILED, globalName)
            }
            dialogVisible.value = false
            await refreshUserTable()  // 刷新表格

          }).catch(() => {
          globalEventbus.emit(Events.MITT.USER.DATA.PATCH.CANCEL, globalName)
          dialogVisible.value = false
        })
      } else {
        dialogVisible.value = false
      }
    }

    // 刷新用户表格
    async function refreshUserTable() {
      tableData.value = []
      isTableLoading.value = true
      const result = await adminUserServiceV1.getUserPreview(userQueryForm) // 加载用户数据概览

      if (result.isSuccess()) {
        // 成功获取用户概览数据
        tableData.value = result.data.users
        tableCount.value = result.data.total

        globalEventbus.emit(
          Events.MITT.USER_MANAGEMENT.LOAD_USERS_PREVIEW.LOAD_SUCCESS,
        )
      } else {
        // 获取用户数据概览失败，使用mitt触发事件
        globalEventbus.emit(
          Events.MITT.USER_MANAGEMENT.LOAD_USERS_PREVIEW.LOAD_FAILED,
          result.message,
        )
      }
      isTableLoading.value = false
    }

    const handleSizeChange = (val) => {
      console.log(`${val} items per page`)
    }
    const handleCurrentChange = (val) => {
      console.log(`current page: ${val}`)
    }


    const onSubmit = async () => {
      await refreshUserTable()  // 刷新表格
    }

    onMounted(() => {
      refreshUserTable() // 加载完成时刷新表格
    })

    return {
      t,
      formattedTableData, // 经过格式化的表单数据
      userQueryForm,  // 用户查询表单
      usernameLabel,
      globalNameLabel,
      operationLabel,  // 操作
      rolesLabel,
      isActiveLabel,
      userIdLabel,
      fuzzyQueryPlaceholder, // 模糊查询表单占位符
      anyStatus,
      activeStatus,
      bannedStatus,
      emptyText,
      isTableLoading,  // 表格是否正在加载
      isPanelLoading,  // 用户详情面板是否正在加载
      dialogVisible,
      targetUserAvatarContext,
      targetUserForm,
      targetUserFormCache,
      roleOptions,  // 权限级别列表
      tableData,
      currentPage,  // 当前页数
      pageSize,  // 页条目数
      paginationSize,
      paginationBackground,
      paginationDisable,
      tableCount,
      onSubmit,
      getIsActiveClassName,
      handleRowClick, // 查询某个用户详情
      handleDialogClose,  // 处理弹窗关闭
      handleUserDelete,  // 处理用户删除
      handleSizeChange,
      handleCurrentChange,
    }
  },
}
</script>
<template>
  <!-- 用户详情 -->
  <div class="user-details-dialog">
    <el-dialog
      v-model="dialogVisible"
      width="500"
      draggable
      :before-close="handleDialogClose"
      style="--el-dialog-border-radius: var(--border-radius); --el-dialog-margin-top: 30vh"

    >
      <el-row v-loading="isPanelLoading" element-loading-background="var(--bg-color-2)">
        <!-- 用户头像 -->
        <el-col :span="6">
          <UserAvatarV2
            :user-avatar-context="targetUserAvatarContext"
            class="user-avatar unselectable"
            :click-to-refresh="true"
            style="width: 100px; height: 100px;"
          />
        </el-col>
        <el-col :span="18">
          <div>
            <el-form :model="targetUserForm"
                     label-width="auto">

              <el-form-item :label="userIdLabel">
                <div class="text-medium">{{targetUserForm.id}}</div>
              </el-form-item>
              <el-form-item :label="usernameLabel">
                <div class="text-medium">{{targetUserForm.username}}</div>
              </el-form-item>
              <el-form-item :label="globalNameLabel">
                <div class="text-medium">{{targetUserForm.global_name}}</div>
              </el-form-item>

              <el-form-item :label="isActiveLabel" style="width: 200px; margin-top: 20px">
                <el-select v-model="targetUserForm.is_active" placeholder="please select your zone">
                  <el-option :label="activeStatus" :value="true" />
                  <el-option :label="bannedStatus" :value="false" />
                </el-select>
              </el-form-item>

              <el-form-item :label="rolesLabel"
                            style="margin-top: 10px;">
                <el-select
                  v-model="targetUserForm.roles"
                  multiple
                  collapse-tags
                  collapse-tags-tooltip
                  placement="bottom"
                  placeholder="Select"
                  style="width: 200px; margin-top: -3px;"
                  class="user-details-dialog"
                >
                  <el-option
                    v-for="item in roleOptions"
                    :key="item.id"
                    :label="item.name"
                    :value="item.name"
                    :disabled="item.disabled"
                  />
                </el-select>
              </el-form-item>

              <el-form-item :label="operationLabel" style="width: 200px; margin-top: 10px">
                <el-button
                  type="danger"
                  @click="handleUserDelete"
                  style="font-size: var(--text-small)"
                >
                  {{ t('view.workspace.UserManagement.delete_user') }}
                </el-button>
              </el-form-item>

            </el-form>
          </div>
        </el-col>
      </el-row>
    </el-dialog>
  </div>

  <!-- 用户检索表单 -->
  <div class="user-table-search">
    <CommonPanel style="height: 52px">
      <el-form :inline="true" :model="userQueryForm">
        <el-form-item :label="globalNameLabel">
          <el-input
            v-model="userQueryForm.global_name"
            :placeholder="fuzzyQueryPlaceholder"
            clearable
            class="text-mini"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item :label="usernameLabel">
          <el-input
            v-model="userQueryForm.username"
            :placeholder="fuzzyQueryPlaceholder"
            clearable
            class="text-mini"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item :label="isActiveLabel">
          <el-select v-model="userQueryForm.is_active" style="width: 130px">
            <el-option :label="anyStatus" :value="-1" />
            <el-option :label="bannedStatus" :value="0" />
            <el-option :label="activeStatus" :value="1" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            @click="onSubmit"
            style="font-size: var(--text-small)"
          >
            {{ t('view.workspace.UserManagement.query') }}
          </el-button>
        </el-form-item>
      </el-form>
    </CommonPanel>
  </div>

  <!-- 用户表格 -->
  <div class="user-table-form">
    <CommonPanel
      style="height: 600px"
      v-loading="isTableLoading"
      element-loading-background="var(--bg-color-2)"
    >
      <el-table
        :data="formattedTableData"
        max-height="500"
        @row-click="handleRowClick"
        :empty-text="emptyText"
      >
        <el-table-column type="index" width="50" />
        <el-table-column prop="username" :label="usernameLabel" width="180" />
        <el-table-column
          prop="global_name"
          :label="globalNameLabel"
          width="180"
        />
        <el-table-column prop="roles" :label="rolesLabel" width="180" />
        <el-table-column prop="is_active" :label="isActiveLabel" />
      </el-table>
    </CommonPanel>
  </div>

  <!-- 分页  -->
  <div class="user-pagination-block">
    <CommonPanel style="height: 52px">
      <el-pagination
        v-model:current-page="userQueryForm.currentPage"
        v-model:page-size="userQueryForm.pageSize"
        :disabled="paginationDisable"
        :background="paginationBackground"
        layout="prev, pager, next, jumper"
        :total="tableCount"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="font-size: var(--text-small)"
      />
    </CommonPanel>
  </div>


</template>
<style scoped>
.el-card {
  width: auto;
  margin-top: 10px;
}
</style>

<style>
.user-table-search .el-card__body,
.user-pagination-block .el-card__body {
  margin-top: 10px;
  margin-left: 10px;
}

.user-table-search .el-input__inner {
  color: var(--text-color);
  font-family: inherit;
}

.user-table-search .el-input__wrapper,
.user-table-search .el-input__wrapper:hover {
  color: var(--text-color);
  font-family: inherit;
  background-color: var(--bg-color);
  border-radius: var(--border-radius);
  box-shadow: none;
}

/* 分页 */
.user-pagination-block .el-pagination {
  --el-pagination-bg-color: var(--bg-color-2);
  --el-pagination-text-color: var(--text-color);
  --el-pagination-border-radius: var(--border-radius);
  --el-pagination-button-color: var(--button-text-color);
  --el-pagination-button-disabled-color: var(--button-text-color);
  --el-pagination-button-disabled-bg-color: var(--bg-color-2);
  --el-pagination-hover-color: var(--text-active-color);
}

.user-pagination-block .el-pager li {
  color: var(--text-color);
  border-radius: var(--border-radius);
  font-size: var(--text-medium);
  min-width: 60px;
}

.user-pagination-block .el-pager li.is-active, .el-pager li:hover {
  color: var(--text-active-color);
}


.user-pagination-block .el-input__inner {
  color: var(--text-color);
  font-family: inherit;
  font-size: var(--text-medium);
}

.user-pagination-block .el-input__wrapper, .el-input__wrapper:hover {
  background-color: var(--bg-color-2);
  border-radius: var(--border-radius);
  box-shadow: none;
}

.user-table-search .el-select {
  --el-select-width: 220px;
}

.user-table-search .el-input {
  --el-input-width: 150px;
  --el-input-bg-color: var(--bg-color);
  --el-input-border-color: var(--popper-border-color);
  --el-input-focus-border-color: var(--popper-border-color);
  --el-input-hover-border-color: var(--popper-border-color);
  --el-input-clear-hover-color: var(--popper-border-color);
  font-size: var(--text-small);
}

.user-table-search .el-form-item__label {
  font-size: var(--text-small);
  color: var(--text-color);
}

.user-table-form .el-card__body {
  padding: 0;
}

.user-table-form .el-table__empty-block {
  background-color: var(--bg-color-2);
  font-size: var(--text-medium);
}

.user-table-form .el-table {
  --el-table-tr-bg-color: var(--bg-color-2); /* 行背景色 */
  --el-table-border-color: var(--bg-color-2); /* 行边界颜色 */
  --el-table-header-bg-color: var(--bg-color-2); /* 表头背景色 */
  --el-table-header-text-color: var(--text-color);
  --el-scrollbar-hover-bg-color: var(--bg-color-2); /* 拖动条悬停背景色 */
  --el-table-row-hover-bg-color: var(--bg-color); /* 行悬停背景色 */
  color: var(--text-color);
  font-size: var(--text-small);
}

.user-table-form .el-table .cell {
  line-height: 25px;
}

.user-details-dialog .el-form-item__label {
  font-size: var(--text-small);
  color: var(--text-color-2);
}

.user-details-dialog .el-dialog__body {
  color: var(--text-color);
}

.user-details-dialog .el-form-item {
  margin-bottom: 0
}

.user-details-dialog .el-tag.el-tag--info, .el-tag.el-tag--info {
  --el-tag-bg-color: var(--bg-color);
  --el-tag-border-color: var(--bg-color-2);
  --el-tag-font-size: var(--text-medium);
  --el-tag-border-radius: var(--border-radius);
  color: var(--text-color);
}

.user-details-dialog .el-dialog {
  --el-dialog-bg-color: var(--bg-color-2);
  --el-dialog-title-font-size: var(--text-medium);
  --el-dialog-content-font-size: var(--text-medium);
}
</style>
