import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/stock-list'
    },
    {
      path: '/stock-list',
      name: 'stockList',
      component: () => import('../views/StockListView.vue'),
      meta: {
        title: '股票清单'
      }
    },
    {
      path: '/stock-detail/:code',
      name: 'stockDetail',
      component: () => import('../views/StockDetailView.vue'),
      props: true,
      meta: {
        title: '个股基本面数据'
      }
    },
    {
      path: '/review-notes',
      name: 'reviewNotes',
      component: () => import('../views/ReviewNotesView.vue'),
      meta: {
        title: '复盘笔记'
      }
    },
    {
      path: '/cost-analysis',
      name: 'costAnalysis',
      component: () => import('../views/CostAnalysisView.vue'),
      meta: {
        title: '成本分析'
      }
    }
  ]
})

// 路由前置守卫，设置页面标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 股票投资清单管理系统` : '股票投资清单管理系统'
  next()
})

export default router