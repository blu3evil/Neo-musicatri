// noinspection JSUnresolvedReference

import { createRouter, createWebHistory } from 'vue-router'
import { store } from '@/storage/index.js'
import { authService } from '@/services/auth-service.js'

// vue路由定义
export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      // 设置模块
      path: '/settings',
      name: 'setting',
      component: () => import('./views/settings/Settings.vue'),  // 主设置页面
      meta: { requireLogin: true },
      children: [
        {
          path: 'appearance',
          name: 'appearance-setting',
          component: () => import('./views/settings/AppearanceSetting.vue')  // 外观设置页面
        },
        {
          path: 'profile',
          name: 'profile-setting',
          component: () => import('./views/settings/ProfileSetting.vue')  // 账户设置界面
        },
        {
          path: 'about',
          name: 'about-setting',
          component: () => import('./views/settings/AboutSetting.vue')  // 账户设置界面
        },
      ]
    },
    {
      // 用户模块
      path: '/login',
      name: 'user-router',
      component: () => import('./views/Login.vue'),
    },
    {
      // oauth登录认证
      path: '/authorized',
      name: 'authorized',
      component: () => import('@/views/Authorized.vue'),
    },
    {
      // 用户功能模块主页
      path: '/workspace',
      name: 'user-home',
      component: () => import('./views/workspace/Workspace.vue'),
      meta: { requireLogin: true },
      children: [
        {
          path: 'dashboard',
          component: () => import('@/views/workspace/dashboard/Dashboard.vue'),
          meta: { requireAdmin: true },
          children: [
            {
              path: 'overview',
              component: () => import('./views/workspace/dashboard/ApplicationOverview.vue'),
            },
            {
              path: 'users',
              component: () => import('./views/workspace/dashboard/UserManagement.vue'),
            },
            {
              path: 'logs',
              component: () => import('./views/workspace/dashboard/LogMonitoring.vue'),
            }
          ]
        },
        {
          path: 'portal',
          component: () => import('./views/workspace/portal/Portal.vue'),
        }
      ]
    },
    {
      // 默认跳转页
      path: '/',
      redirect: '/login'
    },
    {
      // 未定义路径
      path: '/:catchAll(.*)',
      component: () => import('./views/NotFound.vue'),
    }
  ]
})

// 路由守卫
router.beforeEach(async (
  to,
  from,
  next) => {

  let requireLogin = to.meta.requireLogin
  let requireAdmin = to.meta.requireAdmin

  if (requireLogin) {  // 登录检查
    if (!authService.verifyLogin()) {
      next('/login')
      return
    }
  }

  if (requireAdmin) {
    if (!authService.verifyAdmin()) {
      next('/workspace/portal')  // 无管理员权限
      return
    }
  }

  next()  // 放行
})

// 跳转助手，封装跳转逻辑
class Navigator {
  // 用户登录页面
  toLogin() {
    return router.push('/login')
  }

  toPortal() {
    return router.push('/workspace/portal')
  }

  toDashboard(page) {
    return router.push(`/workspace/dashboard/${page}`)
  }

  toDashboardHistory() {
    const activeDashboardMenuItem = store.getters.activeDashboardMenuItem
    return router.push(`/workspace/dashboard/${activeDashboardMenuItem}`)
  }

  // 用户功能模块主页
  toWorkspace() {
    return router.push('/workspace')
  }

  toWorkspaceHistory() {
    const activeWorkspaceMenuItem = store.getters.activeWorkspaceMenuItem
    return router.push(`/workspace/${activeWorkspaceMenuItem}`)
  }

  toSetting(page) {
    return router.push(`/settings/${page}`)
  }

  // 转到设置页面
  toSettingHistory() {
    const activeSettingMenuItem = store.getters.activeSettingMenuItem
    return router.push(`/settings/${activeSettingMenuItem}`)
  }
}

export const navigator = new Navigator()
