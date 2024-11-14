import { createRouter, createWebHistory } from 'vue-router'

// vue路由定义
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      // 设置模块
      path: '/settings',
      name: 'setting',
      component: () => import('./views/AppSetting.vue'),  // 主设置页面
      children: [
        {
          path: 'appearance',
          name: 'appearance-setting',
          component: () => import('./views/AppearanceSetting.vue')  // 外观设置页面
        },
        {
          path: 'profile',
          name: 'profile-setting',
          component: () => import('./views/ProfileSetting.vue')  // 账户设置界面
        }
      ]
    },
    {
      // 用户模块
      path: '/user',
      name: 'user-router',
      children: [
        {
          path: 'login',
          name: 'login',
          component: () => import('./views/UserLogin.vue'),
        },
        {
          // 用户主页
          path: 'home',
          name: 'user-home',
          component: () => import('./views/UserHome.vue'),
        }
      ]
    },
    {
      // 管理员模块
      path: '/admin',
      name: 'admin-route',
      children: [
        {
          // 管理员登录页面
          path: 'login',
          name: 'admin-login',
          component: () => import('./views/AdminLogin.vue'),
        },
        {
          // 管理员仪表盘
          path: 'dashboard',
          name: 'admin-dashboard',
          component: () => import('./views/AdminDashboard.vue'),
        }
      ]
    },
    {
      // 前端api接口模块
      path: '/api',
      name: 'auth-route',
      children: [
        {
          // 认证模块
          path: 'v1',
          name: 'version1',
          children: [
            {
              path: 'auth',
              children: [
                {
                  path: 'discord',
                  children: [
                    {
                      // discord oauth认证回调
                      path: 'authorized',
                      component: () => import('@/views/UserLoginCallback.vue'),
                    }
                  ]
                },
              ]
            }
          ]
        }
      ]
    },
    {
      // 默认跳转页
      path: '/',
      redirect: '/user/login'
    }
  ]
})

export default router
