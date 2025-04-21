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
          path: 'portal',
          component: () => import('./views/workspace/portal/Portal.vue'),
        },
        {
          path: 'app-management',  // 应用面板
          component: () => import('@/views/workspace/app-management/AppManagement.vue'),
          meta: { requireAdmin: true },
          children: [
            {
              path: 'overview',
              component: () => import('@/views/workspace/app-management/Overview.vue'),
            },
            {
              path: 'logs',
              component: () => import('@/views/workspace/app-management/LogMonitoring.vue'),
            }
          ]
        },
        {
          path: 'user-management',  // 用户面板
          component: () => import('@/views/workspace/user-management/UserManagement.vue'),
          meta: { requireAdmin: true },
          children: [
            {
              path: 'overview',
              component: () => import('./views/workspace/user-management/Overview.vue'),
            },
            {
              path: 'management',
              component: () => import('./views/workspace/user-management/Management.vue'),
            },
          ]
        },
        {
          path: 'musiclib-management',  // 曲库面板
          component: () => import('@/views/workspace/musiclib-management/MusiclibManagement.vue'),
          meta: { requireAdmin: true },
          children: [
            {
              path: 'overview',
              component: () => import('./views/workspace/musiclib-management/Overview.vue'),
            },
          ]
        },
        {
          path: 'bot-management',  // 机器人面板
          component: () => import('./views/workspace/bot-management/BotManagement.vue'),
          meta: { requireAdmin: true },
          children: [
            {
              path: 'overview',
              component: () => import('./views/workspace/bot-management/Overview.vue'),
            },
          ]
        },
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
    if (!authService.checkLogin()) {
      next('/login')
      return
    }
  }

  if (requireAdmin) {
    if (!authService.checkRole('admin')) {
      next('/workspace/portal')  // 无管理员权限
      return
    }
  }
  next()  // 放行
})

class Navigator {
  // 用户登录页面
  toLogin() {
    return router.push('/login')
  }

  toPortal() {
    return router.push('/workspace/portal')
  }

  toAppManagement(page) {
    return router.push(`/workspace/app-management/${page}`)
  }

  toUserManagement(page) {
    return router.push(`/workspace/user-management/${page}`)
  }

  toMusicLibManagement(page) {
    return router.push(`/workspace/musiclib-management/${page}`)
  }

  toBotManagement(page) {
    return router.push(`/workspace/bot-management/${page}`)
  }

  toSettings(page) {
    return router.push(`/settings/${page}`)
  }

  toWorkspace = async (page) => {
    switch (page) {
      case 'app-management': await this.toAppManagementHistory(); break;
      case 'user-management': await this.toUserManagementHistory(); break;
      case 'musiclib-management': await this.toMusiclibManagementHistory(); break;
      case 'bot-management': await this.toBotManagementHistory(); break;
      default: await this.toPortal()
    }
  }

  toWorkspaceHistory() {
    const history = store.getters.history.workspaceHistory
    return this.toWorkspace(history)
  }

  toAppManagementHistory() {
    const history = store.getters.history.appManagementHistory
    return router.push(`/workspace/app-management/${history}`)
  }

  toBotManagementHistory() {
    const history = store.getters.history.botManagementHistory
    return router.push(`/workspace/bot-management/${history}`)
  }

  toUserManagementHistory() {
    const history = store.getters.history.userManagementHistory
    return router.push(`/workspace/user-management/${history}`)
  }

  toMusiclibManagementHistory() {
    const history = store.getters.history.musiclibManagementHistory
    return router.push(`/workspace/musiclib-management/${history}`)
  }

  // 转到设置页面
  toSettingsHistory() {
    const history = store.getters.history.settingsHistory
    return router.push(`/settings/${history}`)
  }
}

export const navigator = new Navigator()
