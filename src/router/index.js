import { createRouter, createWebHistory } from 'vue-router'

// 动态导入组件
const StockListView = () => import('../views/StockListView.vue')
const StockDetailView = () => import('../views/StockDetailView.vue')
const ReviewNotesView = () => import('../views/ReviewNotesView.vue')
const MarketOverviewView = () => import('../views/MarketOverviewView.vue')
const SettingsView = () => import('../views/SettingsView.vue')
const PositionAnalysisView = () => import('../views/PositionAnalysisView.vue')

const routes = [
  {
    path: '/',
    redirect: '/stock-list'
  },
  {
    path: '/stock-list',
    name: 'StockList',
    component: StockListView,
    meta: {
      title: '股票清单'
    }
  },
  {
    path: '/stock-detail/:code',
    name: 'StockDetail',
    component: StockDetailView,
    props: true,
    meta: {
      title: '股票详情'
    }
  },
  {
    path: '/market-overview',
    name: 'MarketOverview',
    component: MarketOverviewView,
    meta: {
      title: '今日大盘'
    }
  },
  {
    path: '/review-notes',
    name: 'ReviewNotes',
    component: ReviewNotesView,
    meta: {
      title: '复盘笔记'
    }
  },
  {
    path: '/position-analysis',
    name: 'PositionAnalysis',
    component: PositionAnalysisView,
    meta: {
      title: '持仓分析'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsView,
    meta: {
      title: '系统设置'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/stock-list'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫，设置页面标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 投资助手` : '投资助手'
  next()
})

export default router