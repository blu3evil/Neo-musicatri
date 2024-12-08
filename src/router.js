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
      meta: { loginRequired: true },
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
      meta: { loginRequired: true },
      children: [
        {
          path: 'dashboard',
          component: () => import('@/views/workspace/dashboard/Dashboard.vue'),
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
router.beforeEach((
  to, from, next) => {
  if (to.meta.loginRequired) {
    if (authService.verifyLogin()) next()
    else next('/login')
  } else next()  // 放行
})

// 跳转助手，封装跳转逻辑
class Navigator {
  // 用户登录页面
  toLogin() {
    return router.push('/login')
  }

  toDashboard() {
    return router.push('/workspace/dashboard')
  }

  toPortal() {
    return router.push('/workspace/portal')
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

  // 转到设置页面
  toSetting() {
    const activeSettingMenuItem = store.getters.activeSettingMenuItem
    return router.push(`/settings/${activeSettingMenuItem}`)
  }
}

export const navigator = new Navigator()
