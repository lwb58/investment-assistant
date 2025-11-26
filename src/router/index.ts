import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue')
  },
  {
    path: '/industry-valuation',
    name: 'industry-valuation',
    component: () => import('@/views/IndustryValuationView.vue')
  },
  {
    path: '/market-data',
    name: 'market-data',
    component: () => import('@/views/MarketDataView.vue')
  },
  {
    path: '/financial-analysis',
    name: 'financial-analysis',
    component: () => import('@/views/FinancialAnalysisView.vue')
  },
  {
    path: '/valuation-decision',
    name: 'valuation-decision',
    component: () => import('@/views/ValuationDecisionView.vue')
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue')
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/RegisterView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router