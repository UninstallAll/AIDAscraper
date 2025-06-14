import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    meta: { requiresAuth: false },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'sites',
        name: 'Sites',
        component: () => import('../views/Sites.vue'),
        meta: { title: '站点管理' }
      },
      {
        path: 'jobs',
        name: 'Jobs',
        component: () => import('../views/Jobs.vue'),
        meta: { title: '爬虫任务' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 修改为直接放行
router.beforeEach((to, from, next) => {
  // 直接放行所有路由
  next()
  
  // 原始代码 - 已注释
  // const authStore = useAuthStore()
  // const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  
  // if (requiresAuth && !authStore.isLoggedIn) {
  //   next('/login')
  // } else {
  //   next()
  // }
})

export default router 