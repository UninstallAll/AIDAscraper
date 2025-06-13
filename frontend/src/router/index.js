import { createRouter, createWebHistory } from 'vue-router'

// 懒加载路由组件
const Dashboard = () => import('../views/Dashboard.vue')
const ArtistList = () => import('../views/ArtistList.vue')
const ArtworkList = () => import('../views/ArtworkList.vue')
const ScraperStatus = () => import('../views/ScraperStatus.vue')
const ScraperConfig = () => import('../views/ScraperConfig.vue')
const WebsiteManager = () => import('../views/WebsiteManager.vue')
const Settings = () => import('../views/Settings.vue')
const NotFound = () => import('../views/NotFound.vue')

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { title: 'Dashboard' }
  },
  {
    path: '/artists',
    name: 'Artists',
    component: ArtistList,
    meta: { title: 'Artists' }
  },
  {
    path: '/artworks',
    name: 'Artworks',
    component: ArtworkList,
    meta: { title: 'Artworks' }
  },
  {
    path: '/scraper-status',
    name: 'ScraperStatus',
    component: ScraperStatus,
    meta: { title: 'Scraper Tasks & Status' }
  },
  {
    path: '/scraper-config',
    name: 'ScraperConfig',
    component: ScraperConfig,
    meta: { title: 'Scraper Configuration' }
  },
  {
    path: '/website-manager',
    name: 'WebsiteManager',
    component: WebsiteManager,
    meta: { title: 'Website Manager' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { title: 'Settings' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { title: 'Page Not Found' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - ArtScraper` : 'ArtScraper'
  next()
})

export default router 