# 投资辅助系统前端应用架构设计

## 1. 前端架构概述

投资辅助系统前端采用现代化的单页应用(SPA)架构，基于Vue 3生态系统构建，采用组件化、模块化和响应式的设计理念。系统通过清晰的分层架构和组件化设计，实现高内聚、低耦合的代码组织，保证系统的可维护性、可扩展性和良好的用户体验。

## 2. 技术栈选择

### 2.1 核心框架与库

| 技术/库 | 版本 | 用途 | 选型理由 |
|--------|------|------|----------|
| Vue.js | 3.x | 前端框架 | 响应式、组件化、轻量级，性能优异，生态成熟 |
| TypeScript | 5.x | 开发语言 | 静态类型检查，提升代码质量和开发效率 |
| Vue Router | 4.x | 路由管理 | 官方路由库，与Vue 3无缝集成 |
| Pinia | 2.x | 状态管理 | Vue官方推荐的轻量级状态管理库，支持TypeScript |
| Element Plus | 2.x | UI组件库 | Vue 3支持的企业级组件库，组件丰富，文档完善 |
| Axios | 1.x | HTTP客户端 | 成熟的HTTP请求库，支持拦截器、取消请求等功能 |
| ECharts | 5.x | 数据可视化 | 功能强大的图表库，支持复杂的数据可视化需求 |
| dayjs | 1.x | 日期处理 | 轻量级日期处理库，API友好，体积小 |
| lodash-es | 4.x | 工具函数库 | 提供丰富的工具函数，优化开发效率 |

### 2.2 构建工具与开发环境

| 工具 | 版本 | 用途 | 选型理由 |
|------|------|------|----------|
| Vite | 5.x | 构建工具 | 极速开发体验，快速热重载，优化的构建输出 |
| Vitest | 2.x | 单元测试 | Vite原生支持的测试框架，与Vite完美集成 |
| Cypress | 13.x | E2E测试 | 现代化的端到端测试框架，提供良好的测试体验 |
| ESLint | 8.x | 代码检查 | 保持代码质量和一致性，提供自定义规则支持 |
| Prettier | 3.x | 代码格式化 | 统一代码风格，提升代码可读性 |
| Stylelint | 16.x | CSS检查 | CSS代码质量检查和格式化 |
| husky + lint-staged | 8.x + 15.x | Git hooks | 提交前代码检查和格式化，保证代码质量 |

## 3. 项目目录结构

### 3.1 基础目录结构

```plaintext
investment-assistant/         # 项目根目录
├── public/                   # 静态资源目录
│   ├── favicon.ico           # 网站图标
│   └── robots.txt            # 爬虫协议文件
├── src/                      # 源代码目录
│   ├── assets/               # 项目资源文件
│   │   ├── images/           # 图片资源
│   │   ├── icons/            # 图标资源
│   │   └── styles/           # 全局样式文件
│   ├── components/           # 公共组件目录
│   │   ├── base/             # 基础UI组件
│   │   ├── business/         # 业务组件
│   │   └── charts/           # 图表组件
│   ├── composables/          # 组合式函数
│   ├── config/               # 配置文件
│   ├── constants/            # 常量定义
│   ├── directives/           # 自定义指令
│   ├── hooks/                # 自定义Hooks
│   ├── layouts/              # 布局组件
│   ├── plugins/              # 插件目录
│   ├── router/               # 路由配置
│   ├── services/             # API服务层
│   ├── stores/               # Pinia状态管理
│   ├── types/                # TypeScript类型定义
│   ├── utils/                # 工具函数
│   ├── views/                # 页面视图组件
│   ├── App.vue               # 根组件
│   └── main.ts               # 入口文件
├── tests/                    # 测试目录
│   ├── unit/                 # 单元测试
│   └── e2e/                  # 端到端测试
├── .vscode/                  # VS Code配置
├── .env                      # 环境变量配置
├── .env.development          # 开发环境配置
├── .env.production           # 生产环境配置
├── .eslintrc.js              # ESLint配置
├── .prettierrc.js            # Prettier配置
├── index.html                # HTML入口文件
├── package.json              # 项目配置和依赖
├── tsconfig.json             # TypeScript配置
├── vite.config.ts            # Vite配置
└── README.md                 # 项目说明文档
```

### 3.2 详细目录说明

#### 3.2.1 src/assets/

- **images/**: 存储项目中使用的图片资源
- **icons/**: SVG图标或其他图标资源
- **styles/**: 全局样式文件，包括：
  - `variables.scss`: 全局变量定义
  - `mixins.scss`: 常用样式混合
  - `reset.scss`: 样式重置
  - `global.scss`: 全局样式规则
  - `theme.scss`: 主题相关样式

#### 3.2.2 src/components/

按功能和类型划分组件：

- **base/**: 基础UI组件，与业务无关
  - `Button.vue`: 按钮组件
  - `Input.vue`: 输入框组件
  - `Card.vue`: 卡片组件
  - `Dialog.vue`: 对话框组件
  - `Table.vue`: 表格组件
  - `Pagination.vue`: 分页组件
  - `Loading.vue`: 加载中组件
  - `Empty.vue`: 空状态组件

- **business/**: 业务组件，包含特定业务逻辑
  - `StockCard.vue`: 股票卡片组件
  - `IndustrySelector.vue`: 行业选择器组件
  - `DateRangePicker.vue`: 日期范围选择器
  - `FinancialIndicator.vue`: 财务指标展示组件
  - `ValuationScore.vue`: 估值评分组件
  - `ComparisonTable.vue`: 对比表格组件

- **charts/**: 图表相关组件
  - `LineChart.vue`: 折线图组件
  - `BarChart.vue`: 柱状图组件
  - `PieChart.vue`: 饼图组件
  - `HeatmapChart.vue`: 热力图组件
  - `CandlestickChart.vue`: K线图组件
  - `RadarChart.vue`: 雷达图组件
  - `MultiChart.vue`: 多图表组合组件

#### 3.2.3 src/composables/

Vue 3组合式函数，按功能划分：

- `useApi.ts`: API请求相关函数
- `useAuth.ts`: 认证相关函数
- `useChart.ts`: 图表配置相关函数
- `useDate.ts`: 日期处理相关函数
- `useDebounce.ts`: 防抖相关函数
- `useLocalStorage.ts`: 本地存储相关函数
- `useLoading.ts`: 加载状态管理函数
- `usePagination.ts`: 分页逻辑处理函数
- `usePermission.ts`: 权限控制相关函数
- `useTheme.ts`: 主题切换相关函数

#### 3.2.4 src/config/

项目配置文件：

- `api.ts`: API接口配置
- `router.ts`: 路由相关配置
- `store.ts`: 状态管理配置
- `theme.ts`: 主题配置
- `mock.ts`: Mock数据配置
- `featureFlags.ts`: 功能开关配置

#### 3.2.5 src/stores/

Pinia状态管理，按模块划分：

- `auth.ts`: 认证状态管理
- `user.ts`: 用户信息状态管理
- `stock.ts`: 股票数据状态管理
- `industry.ts`: 行业数据状态管理
- `market.ts`: 市场数据状态管理
- `financial.ts`: 财务数据状态管理
- `valuation.ts`: 估值数据状态管理
- `ui.ts`: UI相关状态管理(如主题、加载状态等)
- `settings.ts`: 系统设置状态管理

#### 3.2.6 src/services/

API服务层，按业务模块划分：

- `api.ts`: API基础配置和请求封装
- `auth.service.ts`: 认证相关API
- `user.service.ts`: 用户相关API
- `stock.service.ts`: 股票相关API
- `industry.service.ts`: 行业相关API
- `market.service.ts`: 市场数据相关API
- `financial.service.ts`: 财务数据相关API
- `valuation.service.ts`: 估值相关API
- `mock.service.ts`: Mock数据服务

#### 3.2.7 src/views/

页面视图组件，按功能模块划分：

- `HomeView.vue`: 首页视图
- `industry/`: 行业估值分析模块
  - `IndustryListView.vue`: 行业列表视图
  - `IndustryDetailView.vue`: 行业详情视图
  - `IndustryComparisonView.vue`: 行业对比视图
- `market/`: 市场数据中心模块
  - `MarketIndexView.vue`: 市场指数视图
  - `HotStocksView.vue`: 热点股票视图
  - `FundFlowView.vue`: 资金流向视图
- `financial/`: 财务分析引擎模块
  - `StockSearchView.vue`: 股票搜索视图
  - `FinancialDetailView.vue`: 财务详情视图
  - `FinancialAnalysisView.vue`: 财务分析视图
- `valuation/`: 估值决策系统模块
  - `ValuationCalculatorView.vue`: 估值计算器视图
  - `ValuationResultView.vue`: 估值结果视图
  - `ScoreAnalysisView.vue`: 评分分析视图
- `user/`: 用户中心模块
  - `LoginView.vue`: 登录视图
  - `RegisterView.vue`: 注册视图
  - `ProfileView.vue`: 个人资料视图
  - `SettingsView.vue`: 设置视图

## 4. 组件化设计方案

### 4.1 组件设计原则

1. **单一职责原则**: 每个组件只负责一个功能点
2. **可复用性**: 设计通用组件，减少代码重复
3. **可配置性**: 组件通过props和事件提供灵活配置
4. **可测试性**: 组件设计易于单元测试
5. **可维护性**: 组件结构清晰，代码可读性高
6. **性能优化**: 避免不必要的重渲染，合理使用虚拟滚动等技术

### 4.2 组件分层策略

#### 4.2.1 展示型组件

- **功能**: 负责UI展示，不包含业务逻辑
- **特点**: 纯函数式，输入props，输出视图
- **例子**: Button、Card、Table等基础组件
- **设计模式**: Props Down, Events Up

```vue
<!-- 展示型组件示例 -->
<template>
  <div class="stock-card" :class="{ 'highlight': highlighted }">
    <h3>{{ stock.name }} ({{ stock.code }})</h3>
    <div class="price">{{ formatPrice(stock.price) }}</div>
    <div class="change" :class="{ 'up': stock.change > 0, 'down': stock.change < 0 }">
      {{ stock.change > 0 ? '+' : '' }}{{ stock.changePercent }}%
    </div>
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { formatPrice } from '@/utils/formatters';

interface StockData {
  code: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
}

const props = defineProps<{
  stock: StockData;
  highlighted?: boolean;
}>();
</script>
```

#### 4.2.2 容器型组件

- **功能**: 负责业务逻辑，状态管理，数据获取
- **特点**: 包含业务逻辑，使用展示型组件
- **例子**: 页面级组件，业务模块容器
- **设计模式**: 容器模式

```vue
<!-- 容器型组件示例 -->
<template>
  <div class="stock-list">
    <div class="header">
      <h2>热门股票</h2>
      <el-select v-model="selectedType" @change="loadStocks">
        <el-option label="涨幅榜" value="up"></el-option>
        <el-option label="跌幅榜" value="down"></el-option>
        <el-option label="换手率榜" value="turnover"></el-option>
      </el-select>
    </div>
    
    <div v-if="loading" class="loading">
      <el-loading-spinner></el-loading-spinner>
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
      <el-button @click="loadStocks">重试</el-button>
    </div>
    
    <div v-else class="stock-grid">
      <stock-card
        v-for="stock in stocks"
        :key="stock.code"
        :stock="stock"
        :highlighted="stock.code === selectedStock"
        @click="selectStock(stock)"
      >
        <div class="extra-info">
          成交量: {{ formatVolume(stock.volume) }}
        </div>
      </stock-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useMarketStore } from '@/stores/market';
import { formatVolume } from '@/utils/formatters';
import StockCard from '@/components/business/StockCard.vue';

const router = useRouter();
const marketStore = useMarketStore();

const selectedType = ref('up');
const loading = ref(false);
const error = ref('');
const selectedStock = ref('');

const stocks = ref([]);

const loadStocks = async () => {
  loading.value = true;
  error.value = '';
  try {
    stocks.value = await marketStore.getHotStocks(selectedType.value);
  } catch (err) {
    error.value = '加载失败，请稍后重试';
    console.error('Failed to load hot stocks:', err);
  } finally {
    loading.value = false;
  }
};

const selectStock = (stock) => {
  selectedStock.value = stock.code;
  router.push(`/financial/detail/${stock.code}`);
};

onMounted(() => {
  loadStocks();
});
</script>
```

#### 4.2.3 高阶组件

- **功能**: 增强组件功能，提供横切关注点
- **特点**: 接收一个组件，返回一个增强的组件
- **例子**: 带权限控制的组件，带缓存的组件
- **设计模式**: 装饰器模式

```typescript
// 高阶组件示例 - 权限控制
import { defineComponent, h } from 'vue';
import { useAuthStore } from '@/stores/auth';

interface WithPermissionProps {
  permission: string;
  fallback?: JSX.Element;
}

export function withPermission<P extends Record<string, any>>(Component: any, requiredPermission: string) {
  return defineComponent<P & WithPermissionProps>({
    name: `WithPermission-${Component.name || 'Component'}`,
    setup(props, { slots }) {
      const authStore = useAuthStore();
      
      const hasPermission = authStore.hasPermission(requiredPermission);
      
      return () => {
        if (hasPermission) {
          return h(Component, props, slots);
        } else if (props.fallback) {
          return props.fallback;
        } else {
          return h('div', { class: 'permission-denied' }, '您没有权限访问此内容');
        }
      };
    }
  });
}
```

### 4.3 组件通信方案

#### 4.3.1 Props/Events 通信

- **适用场景**: 父子组件通信
- **优点**: 明确的数据流，易于追踪
- **实现**: props向下传递数据，events向上传递事件

```vue
<!-- 父组件 -->
<template>
  <child-component 
    :data="parentData"
    @update="handleUpdate"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ChildComponent from './ChildComponent.vue';

const parentData = ref('Hello from parent');

const handleUpdate = (newData) => {
  parentData.value = newData;
};
</script>

<!-- 子组件 -->
<template>
  <div>
    <p>{{ data }}</p>
    <button @click="updateData">Update</button>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';

const props = defineProps<{
  data: string;
}>();

const emit = defineEmits<{
  update: [newData: string];
}>();

const updateData = () => {
  emit('update', 'Updated data from child');
};
</script>
```

#### 4.3.2 Provide/Inject 通信

- **适用场景**: 跨多层级组件通信
- **优点**: 避免props drilling问题
- **实现**: provide提供数据，inject注入数据

```vue
<!-- 祖先组件 -->
<template>
  <div>
    <child-component />
  </div>
</template>

<script setup lang="ts">
import { ref, provide } from 'vue';
import ChildComponent from './ChildComponent.vue';

const theme = ref('light');

provide('theme', theme);
provide('setTheme', (newTheme) => {
  theme.value = newTheme;
});
</script>

<!-- 后代组件 -->
<template>
  <div :class="`theme-${theme}`">
    <button @click="setTheme('dark')">切换到深色主题</button>
    <button @click="setTheme('light')">切换到浅色主题</button>
  </div>
</template>

<script setup lang="ts">
import { inject, Ref } from 'vue';

const theme = inject<Ref<string>>('theme');
const setTheme = inject<(theme: string) => void>('setTheme');
</script>
```

#### 4.3.3 Pinia 状态管理

- **适用场景**: 全局状态管理，复杂业务逻辑
- **优点**: 集中管理状态，易于调试
- **实现**: 定义store，组件通过store访问和修改状态

```typescript
// stores/stock.ts
import { defineStore } from 'pinia';
import { stockService } from '@/services/stock.service';

export interface Stock {
  code: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
}

export const useStockStore = defineStore('stock', {
  state: () => ({
    stocks: [] as Stock[],
    selectedStock: null as Stock | null,
    loading: false,
    error: null as string | null
  }),
  
  getters: {
    upStocks: (state) => state.stocks.filter(stock => stock.changePercent > 0),
    downStocks: (state) => state.stocks.filter(stock => stock.changePercent < 0),
    totalStocks: (state) => state.stocks.length
  },
  
  actions: {
    async fetchStocks() {
      this.loading = true;
      this.error = null;
      try {
        this.stocks = await stockService.getStocks();
      } catch (err) {
        this.error = '加载股票数据失败';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    
    selectStock(stock: Stock) {
      this.selectedStock = stock;
    },
    
    async refreshStock(stockCode: string) {
      try {
        const updatedStock = await stockService.getStockDetail(stockCode);
        const index = this.stocks.findIndex(s => s.code === stockCode);
        if (index !== -1) {
          this.stocks[index] = updatedStock;
        }
        if (this.selectedStock?.code === stockCode) {
          this.selectedStock = updatedStock;
        }
      } catch (err) {
        console.error(`刷新股票 ${stockCode} 失败:`, err);
      }
    }
  }
});

// 组件中使用
<script setup lang="ts">
import { useStockStore } from '@/stores/stock';
import { onMounted } from 'vue';

const stockStore = useStockStore();

onMounted(() => {
  stockStore.fetchStocks();
});

const handleSelectStock = (stock) => {
  stockStore.selectStock(stock);
};
</script>
```

## 5. 响应式设计方案

### 5.1 设计原则

- **移动优先**: 从移动设备开始设计，然后扩展到更大屏幕
- **断点设计**: 使用媒体查询定义不同屏幕尺寸的布局
- **弹性布局**: 使用Flexbox和Grid创建灵活的布局结构
- **响应式组件**: 组件能根据屏幕尺寸自动调整
- **性能优化**: 在移动设备上减少不必要的资源加载

### 5.2 断点设计

| 断点名称 | 屏幕宽度 | 设备类型 | 设计策略 |
|---------|---------|---------|----------|
| xs | < 576px | 手机 (竖屏) | 单列布局，简化导航 |
| sm | ≥ 576px | 手机 (横屏) | 适当增加内容密度 |
| md | ≥ 768px | 平板 (竖屏) | 两列布局，展开部分菜单 |
| lg | ≥ 992px | 平板 (横屏) / 小屏桌面 | 三列布局，完整导航 |
| xl | ≥ 1200px | 桌面 | 四列布局，充分利用空间 |
| xxl | ≥ 1600px | 大屏桌面 | 更宽布局，增加图表复杂度 |

### 5.3 实现方案

#### 5.3.1 CSS变量

```scss
// src/assets/styles/variables.scss
:root {
  // 断点变量
  --breakpoint-xs: 0;
  --breakpoint-sm: 576px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 992px;
  --breakpoint-xl: 1200px;
  --breakpoint-xxl: 1600px;
  
  // 间距变量
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  // 字体大小
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-md: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;
  --font-size-xxl: 24px;
  
  // 容器宽度
  --container-sm: 540px;
  --container-md: 720px;
  --container-lg: 960px;
  --container-xl: 1140px;
  --container-xxl: 1540px;
}
```

#### 5.3.2 响应式布局混合

```scss
// src/assets/styles/mixins.scss
@mixin responsive($breakpoint) {
  @if $breakpoint == xs {
    @media (max-width: map-get($breakpoints, xs)) { @content; }
  }
  @else if $breakpoint == sm {
    @media (min-width: map-get($breakpoints, sm)) { @content; }
  }
  @else if $breakpoint == md {
    @media (min-width: map-get($breakpoints, md)) { @content; }
  }
  @else if $breakpoint == lg {
    @media (min-width: map-get($breakpoints, lg)) { @content; }
  }
  @else if $breakpoint == xl {
    @media (min-width: map-get($breakpoints, xl)) { @content; }
  }
  @else if $breakpoint == xxl {
    @media (min-width: map-get($breakpoints, xxl)) { @content; }
  }
}

// 使用示例
.container {
  width: 100%;
  padding-right: var(--spacing-md);
  padding-left: var(--spacing-md);
  margin-right: auto;
  margin-left: auto;
  
  @include responsive(sm) {
    max-width: var(--container-sm);
  }
  
  @include responsive(md) {
    max-width: var(--container-md);
  }
  
  @include responsive(lg) {
    max-width: var(--container-lg);
  }
  
  @include responsive(xl) {
    max-width: var(--container-xl);
  }
  
  @include responsive(xxl) {
    max-width: var(--container-xxl);
  }
}
```

#### 5.3.3 响应式组件实现

```vue
<template>
  <div class="dashboard">
    <!-- 移动端导航 -->
    <el-drawer
      v-model="mobileDrawerVisible"
      direction="left"
      size="80%"
      :with-header="false"
    >
      <mobile-nav-menu />
    </el-drawer>
    
    <div class="header">
      <el-button 
        icon="el-icon-menu" 
        class="menu-toggle"
        @click="mobileDrawerVisible = true"
      ></el-button>
      <h1 class="title">投资辅助系统</h1>
      <user-profile />
    </div>
    
    <div class="main-container">
      <!-- 桌面端侧边栏 -->
      <aside class="sidebar" :class="{ 'collapsed': isSidebarCollapsed }">
        <desktop-nav-menu @toggle="toggleSidebar" />
      </aside>
      
      <!-- 内容区域 -->
      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useMediaQuery } from '@vueuse/core';
import MobileNavMenu from './MobileNavMenu.vue';
import DesktopNavMenu from './DesktopNavMenu.vue';
import UserProfile from './UserProfile.vue';

// 使用媒体查询检测屏幕尺寸
const isMobile = useMediaQuery('(max-width: 768px)');
const isMedium = useMediaQuery('(min-width: 769px) and (max-width: 1024px)');
const isLarge = useMediaQuery('(min-width: 1025px)');

const mobileDrawerVisible = ref(false);
const isSidebarCollapsed = ref(false);

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
};

// 监听屏幕尺寸变化
const handleResize = () => {
  if (isMobile.value) {
    mobileDrawerVisible.value = false;
  }
};

onMounted(() => {
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped lang="scss">
.dashboard {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.header {
  display: flex;
  align-items: center;
  padding: var(--spacing-md);
  background-color: var(--color-primary);
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.menu-toggle {
  display: block;
  background: transparent;
  border: none;
  color: white;
  margin-right: var(--spacing-md);
}

.title {
  flex: 1;
  margin: 0;
  font-size: var(--font-size-lg);
}

.main-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 240px;
  background-color: var(--color-background);
  border-right: 1px solid var(--color-border);
  transition: width 0.3s ease;
  overflow-y: auto;
  
  &.collapsed {
    width: 64px;
  }
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md);
}

// 响应式样式
@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
  
  .content {
    padding: var(--spacing-sm);
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .menu-toggle {
    display: none;
  }
  
  .sidebar {
    width: 200px;
    
    &.collapsed {
      width: 56px;
    }
  }
}

@media (min-width: 1025px) {
  .menu-toggle {
    display: none;
  }
}
</style>
```

## 6. 性能优化策略

### 6.1 构建优化

- **代码分割**: 使用动态导入实现路由级代码分割
- **Tree Shaking**: 移除未使用的代码
- **懒加载**: 路由组件、大型组件懒加载
- **资源压缩**: JS、CSS、图片压缩
- **预加载**: 关键资源预加载
- **CDN加速**: 静态资源通过CDN分发

```javascript
// 路由懒加载示例
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/industry',
    name: 'Industry',
    component: () => import('@/views/industry/IndustryListView.vue'),
    meta: { title: '行业估值分析' }
  },
  {
    path: '/market',
    name: 'Market',
    component: () => import('@/views/market/MarketIndexView.vue'),
    meta: { title: '市场数据中心' }
  },
  {
    path: '/financial/:stockCode',
    name: 'FinancialDetail',
    component: () => import('@/views/financial/FinancialDetailView.vue'),
    meta: { title: '财务详情' },
    props: true
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
```

### 6.2 运行时优化

- **虚拟滚动**: 处理大量数据列表
- **防抖节流**: 优化用户交互
- **缓存策略**: 缓存计算结果和API响应
- **组件复用**: 优化长列表渲染
- **避免不必要的重渲染**: 合理使用计算属性、监听
- **按需加载**: 第三方库按需引入

```vue
<!-- 虚拟滚动示例 -->
<template>
  <div class="stock-list-container">
    <el-input 
      v-model="searchKeyword"
      placeholder="搜索股票代码或名称"
      prefix-icon="el-icon-search"
      class="search-input"
    />
    
    <el-empty v-if="filteredStocks.length === 0" description="暂无数据" />
    
    <virtual-list
      v-else
      class="virtual-list"
      :data-key="'code'"
      :data-sources="filteredStocks"
      :data-component="itemComponent"
      :estimate-size="80"
      :item-class="'stock-item'"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useStockStore } from '@/stores/stock';
import VirtualList from 'vue-virtual-scroller/src/components/VirtualList.vue';
import StockItem from './StockItem.vue';

const stockStore = useStockStore();
const searchKeyword = ref('');
const itemComponent = StockItem;

const filteredStocks = computed(() => {
  if (!searchKeyword.value) {
    return stockStore.stocks;
  }
  
  const keyword = searchKeyword.value.toLowerCase();
  return stockStore.stocks.filter(stock => 
    stock.code.toLowerCase().includes(keyword) ||
    stock.name.toLowerCase().includes(keyword)
  );
});
</script>

<style scoped>
.stock-list-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.search-input {
  margin-bottom: var(--spacing-md);
}

.virtual-list {
  flex: 1;
  overflow: auto;
}

.stock-item {
  height: 80px;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  
  &:hover {
    background-color: var(--color-background-light);
  }
}
</style>
```

### 6.3 网络优化

- **HTTP/2**: 使用HTTP/2协议
- **API设计**: 合理设计API，减少请求次数
- **数据压缩**: 使用gzip/brotli压缩响应数据
- **缓存控制**: 合理设置Cache-Control头
- **批量请求**: 合并多个小请求为一个大请求
- **WebSocket**: 实时数据使用WebSocket

```typescript
// 批量请求示例
// services/api.ts
import axios from 'axios';

// 批量获取股票详情
async function getStocksDetailBatch(stockCodes: string[]) {
  // 将股票代码分批，每批最多50个
  const batchSize = 50;
  const batches = [];
  
  for (let i = 0; i < stockCodes.length; i += batchSize) {
    batches.push(stockCodes.slice(i, i + batchSize));
  }
  
  // 并行请求所有批次
  const promises = batches.map(batch => 
    axios.post('/api/v1/stocks/batch', { codes: batch })
  );
  
  // 等待所有请求完成并合并结果
  const results = await Promise.all(promises);
  const stockDetails = results.flatMap(result => result.data.data);
  
  return stockDetails;
}

export const apiService = {
  getStocksDetailBatch
};
```

## 7. 测试策略

### 7.1 测试类型

- **单元测试**: 测试组件、函数的最小单元
- **组件测试**: 测试单个组件的行为和输出
- **集成测试**: 测试组件之间的交互
- **端到端测试**: 模拟用户操作的完整测试流程

### 7.2 测试框架配置

```javascript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './tests/setup.ts',
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
});
```

### 7.3 单元测试示例

```typescript
// tests/unit/formatters.test.ts
import { describe, it, expect } from 'vitest';
import { formatPrice, formatVolume, formatPercent } from '@/utils/formatters';

describe('Formatters', () => {
  describe('formatPrice', () => {
    it('should format price correctly with 2 decimal places', () => {
      expect(formatPrice(1234.5678)).toBe('1234.57');
    });
    
    it('should format negative price correctly', () => {
      expect(formatPrice(-123.45)).toBe('-123.45');
    });
    
    it('should format large price with thousand separator', () => {
      expect(formatPrice(1000000)).toBe('1,000,000.00');
    });
  });
  
  describe('formatVolume', () => {
    it('should format volume less than 10000 correctly', () => {
      expect(formatVolume(1234)).toBe('1234');
    });
    
    it('should format volume between 10000 and 100000000', () => {
      expect(formatVolume(12345)).toBe('1.23万');
    });
    
    it('should format volume larger than 100000000', () => {
      expect(formatVolume(123456789)).toBe('1.23亿');
    });
  });
});
```

### 7.4 组件测试示例

```typescript
// tests/unit/components/StockCard.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import StockCard from '@/components/business/StockCard.vue';

describe('StockCard', () => {
  let wrapper;
  const stockData = {
    code: '600519',
    name: '贵州茅台',
    price: 1823.00,
    change: 18.23,
    changePercent: 1.01
  };
  
  beforeEach(() => {
    wrapper = mount(StockCard, {
      props: {
        stock: stockData
      }
    });
  });
  
  it('should render stock information correctly', () => {
    expect(wrapper.text()).toContain('贵州茅台');
    expect(wrapper.text()).toContain('600519');
    expect(wrapper.text()).toContain('1823.00');
    expect(wrapper.text()).toContain('1.01%');
  });
  
  it('should apply correct class for positive change', () => {
    expect(wrapper.find('.change').classes()).toContain('up');
  });
  
  it('should apply highlighted class when highlighted prop is true', () => {
    wrapper.setProps({ highlighted: true });
    expect(wrapper.classes()).toContain('highlight');
  });
  
  it('should emit click event when clicked', async () => {
    await wrapper.trigger('click');
    expect(wrapper.emitted('click')).toBeTruthy();
  });
});
```

## 8. 部署与CI/CD

### 8.1 构建配置

```javascript
// vite.config.ts
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    vue(),
    // 构建分析插件
    visualizer({
      open: true,
      filename: 'stats.html'
    })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  build: {
    // 构建优化
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    // 资源优化
    assetsInlineLimit: 4096,
    // 代码分割
    rollupOptions: {
      output: {
        manualChunks: {
          vue: ['vue', 'vue-router', 'pinia'],
          elementPlus: ['element-plus'],
          echarts: ['echarts'],
          lodash: ['lodash-es'],
          dayjs: ['dayjs']
        }
      }
    }
  }
});
```

### 8.2 CI/CD配置 (GitHub Actions)

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run lint
        run: npm run lint
      
      - name: Run tests
        run: npm test
  
  build:
    name: Build Application
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build application
        run: npm run build
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist
  
  deploy:
    name: Deploy to Production
    if: github.ref == 'refs/heads/main'
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: dist
          path: dist
      
      - name: Deploy to server
        uses: easingthemes/ssh-deploy@v4.0.1
        with:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          ARGS: '-rltgoDzvO --delete'
          SOURCE: 'dist/'
          REMOTE_HOST: ${{ secrets.REMOTE_HOST }}
          REMOTE_USER: ${{ secrets.REMOTE_USER }}
          TARGET: ${{ secrets.REMOTE_TARGET }}
```

## 9. 代码规范与最佳实践

### 9.1 TypeScript规范

- **接口命名**: 使用 `I` 前缀或 `Props`/`Params`/`Result` 后缀
- **类型命名**: PascalCase，常量使用 UPPER_CASE
- **避免 any**: 尽量使用具体类型，减少 any 的使用
- **可选链和空值合并**: 使用 `?.` 和 `??` 简化代码
- **类型保护**: 使用类型守卫函数处理复杂类型判断

### 9.2 Vue 3 最佳实践

- **Composition API**: 优先使用 Composition API
- **setup 语法糖**: 使用 `<script setup lang="ts">` 简化代码
- **响应式数据**: 合理使用 `ref`/`reactive`/`computed`/`watch`
- **事件命名**: 使用 `kebab-case` 命名事件
- **属性命名**: Props 使用 `camelCase`，Attributes 使用 `kebab-case`
- **组件命名**: 组件名使用 PascalCase，文件名使用 PascalCase
- **避免内联样式**: 使用 CSS 类或样式对象
- **避免深层选择器**: 使用 `::v-deep` 或 `:deep()` 代替 `/deep/`

### 9.3 项目结构最佳实践

- **按功能模块组织**: 相关功能的文件放在同一目录
- **组件拆分**: 合理拆分组件，职责单一
- **状态管理**: 复杂状态使用 Pinia，简单状态使用组件内部状态
- **工具函数**: 抽离通用工具函数到 utils 目录
- **API 封装**: 将 API 请求封装到 services 层
- **类型定义**: 创建 types 目录统一管理类型定义

## 10. 未来扩展性考虑

### 10.1 功能扩展

- **插件系统**: 设计插件机制支持功能扩展
- **主题定制**: 支持多主题定制
- **国际化支持**: 预留 i18n 国际化扩展点
- **图表类型扩展**: 设计可扩展的图表组件系统
- **数据源扩展**: 支持多种数据源接入

### 10.2 技术升级

- **Web Components**: 未来可考虑支持 Web Components
- **WebAssembly**: 复杂计算可考虑使用 WebAssembly 优化性能
- **PWA 支持**: 增强离线体验
- **微前端架构**: 大规模应用可考虑微前端架构

### 10.3 性能扩展

- **WebWorkers**: 复杂计算使用 WebWorkers 避免阻塞主线程
- **Service Workers**: 缓存策略优化
- **WebGL**: 大型数据可视化考虑使用 WebGL 加速
- **SSR 支持**: 未来可考虑服务端渲染提升首屏加载性能