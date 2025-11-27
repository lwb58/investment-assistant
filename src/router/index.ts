import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: {
      title: '智能投资助手 - 首页'
    }
  },
  {
    path: '/market-data',
    name: 'marketData',
    component: () => import('@/views/MarketDataView.vue'),
    meta: {
      title: '市场行情 - 智能投资助手'
    }
  },
  {
    path: '/stock/search',
    name: 'stockSearch',
    component: () => import('@/views/StockSearchView.vue'),
    meta: {
      title: '股票搜索 - 智能投资助手'
    }
  },
  {
    path: '/stock/detail/:code',
    name: 'stockDetail',
    component: () => import('@/views/StockDetailView.vue'),
    meta: {
      title: '股票详情 - 智能投资助手'
    }
  },
  {
    path: '/stock/analysis/:code',
    name: 'stockAnalysis',
    component: () => import('@/views/StockAnalysisView.vue'),
    meta: {
      title: '股票分析 - 智能投资助手'
    }
  },
  {
    path: '/favorite-stocks',
    name: 'favoriteStocks',
    component: () => import('@/views/FavoriteStocksView.vue'),
    meta: {
      title: '关注股票 - 智能投资助手'
    }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: {
      title: '个人中心 - 智能投资助手'
    }
  },
  // {
  //   path: '/about',
  //   name: 'about',
  //   component: () => import('@/views/AboutView.vue'),
  //   meta: {
  //     title: '关于我们 - 智能投资助手'
  //   }
  // }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫，设置页面标题
router.beforeEach((to, _from, next) => {
  document.title = to.meta.title as string || '智能投资助手'
  next()
})

export default router