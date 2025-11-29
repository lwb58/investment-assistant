<template>
  <div class="market-overview-container">
    <!-- 大盘概览 -->
    <div class="market-index-card">
      <h2 class="card-title">
        <i class="el-icon-s-data"></i> 大盘概览
      </h2>
      <div class="index-grid">
        <!-- 上证指数 -->
        <div class="index-item">
          <div class="index-name">上证指数</div>
          <div class="index-value">{{ shIndex }}</div>
          <div class="index-change" :class="shChange >= 0 ? 'rise' : 'fall'">
            {{ shChange >= 0 ? '+' : '' }}{{ shChange }} ({{ shChange >= 0 ? '+' : '' }}{{ shChangeRate }}%)
          </div>
        </div>
        <!-- 深证成指 -->
        <div class="index-item">
          <div class="index-name">深证成指</div>
          <div class="index-value">{{ szIndex }}</div>
          <div class="index-change" :class="szChange >= 0 ? 'rise' : 'fall'">
            {{ szChange >= 0 ? '+' : '' }}{{ szChange }} ({{ szChange >= 0 ? '+' : '' }}{{ szChangeRate }}%)
          </div>
        </div>
        <!-- 创业板指 -->
        <div class="index-item">
          <div class="index-name">创业板指</div>
          <div class="index-value">{{ cyIndex }}</div>
          <div class="index-change" :class="cyChange >= 0 ? 'rise' : 'fall'">
            {{ cyChange >= 0 ? '+' : '' }}{{ cyChange }} ({{ cyChange >= 0 ? '+' : '' }}{{ cyChangeRate }}%)
          </div>
        </div>
        <!-- 市场统计 -->
        <div class="index-item">
          <div class="index-name">上涨家数</div>
          <div class="index-value rise">{{ upStocks }}</div>
          <div class="index-desc">市场活跃度</div>
        </div>
        <div class="index-item">
          <div class="index-name">下跌家数</div>
          <div class="index-value fall">{{ downStocks }}</div>
          <div class="index-desc">市场调整度</div>
        </div>
        <div class="index-item">
          <div class="index-name">成交额</div>
          <div class="index-value">{{ totalAmount }} 亿元</div>
          <div class="index-desc">市场资金量</div>
        </div>
      </div>
      <div class="update-time">更新时间：{{ updateTime }}</div>
    </div>

    <!-- 行业涨跌幅TOP5 -->
    <div class="industry-concept-card industry-card">
      <h2 class="card-title">
        <i class="el-icon-industry"></i> 行业涨跌幅TOP5
      </h2>
      <div class="top5-grid">
        <!-- 行业涨幅TOP5 -->
        <div class="top5-list">
          <h3 class="list-title rise">
            <i class="el-icon-arrow-up"></i> 涨幅榜
          </h3>
          <div class="list-container">
            <div v-if="industryUp.length === 0" class="empty-tip">暂无数据</div>
            <div v-for="(item, index) in industryUp" :key="`industry-up-${index}`" class="list-item">
              <div class="rank industry-rank">{{ index + 1 }}</div>
              <div class="info">
                <div class="name">{{ item.name }}</div>
                <!-- 修复：添加空值判断，无数据时显示0.00% -->
<div class="leader-stock">领涨股：{{ item.leaderStock }}({{ item.leaderStockCode }})<span class="rise"> {{ (Number(item.leaderStockChange) ?? 0) >= 0 ? '+' : '' }}{{ (Number(item.leaderStockChange) ?? 0).toFixed(2) }}%</span></div>
              </div>
              <div class="change-rate rise">{{ item.changeRate >= 0 ? '+' : '' }}{{ item.changeRate }}%</div>
            </div>
          </div>
        </div>
        <!-- 行业跌幅TOP5 -->
        <div class="top5-list">
          <h3 class="list-title fall">
            <i class="el-icon-arrow-down"></i> 跌幅榜
          </h3>
          <div class="list-container">
            <div v-if="industryDown.length === 0" class="empty-tip">暂无数据</div>
            <div v-for="(item, index) in industryDown" :key="`industry-down-${index}`" class="list-item">
              <div class="rank industry-rank">{{ index + 1 }}</div>
              <div class="info">
                <div class="name">{{ item.name }}</div>
                <!-- 修复：添加空值判断 -->
<div class="leader-stock">领跌股：{{ item.leaderStock }}({{ item.leaderStockCode }})<span class="fall"> {{ (Number(item.leaderStockChange) ?? 0) >= 0 ? '+' : '' }}{{ (Number(item.leaderStockChange) ?? 0).toFixed(2) }}%</span></div>
              </div>
              <div class="change-rate fall">{{ item.changeRate >= 0 ? '+' : '' }}{{ item.changeRate }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 概念涨跌幅TOP5 -->
    <div class="industry-concept-card concept-card">
      <h2 class="card-title">
        <i class="el-icon-lightbulb"></i> 概念涨跌幅TOP5
      </h2>
      <div class="top5-grid">
        <!-- 概念涨幅TOP5 -->
        <div class="top5-list">
          <h3 class="list-title rise">
            <i class="el-icon-arrow-up"></i> 涨幅榜
          </h3>
          <div class="list-container">
            <div v-if="conceptUp.length === 0" class="empty-tip">暂无数据</div>
            <div v-for="(item, index) in conceptUp" :key="`concept-up-${index}`" class="list-item">
              <div class="rank concept-rank">{{ index + 1 }}</div>
              <div class="info">
                <div class="name">{{ item.name }}</div>
                <!-- 修复：添加空值判断 -->
<div class="leader-stock">领涨股：{{ item.leaderStock }}({{ item.leaderStockCode }})<span class="rise"> {{ (Number(item.leaderStockChange) ?? 0) >= 0 ? '+' : '' }}{{ (Number(item.leaderStockChange) ?? 0).toFixed(2) }}%</span></div>
              </div>
              <div class="change-rate rise">{{ item.changeRate >= 0 ? '+' : '' }}{{ item.changeRate }}%</div>
            </div>
          </div>
        </div>
        <!-- 概念跌幅TOP5 -->
        <div class="top5-list">
          <h3 class="list-title fall">
            <i class="el-icon-arrow-down"></i> 跌幅榜
          </h3>
          <div class="list-container">
            <div v-if="conceptDown.length === 0" class="empty-tip">暂无数据</div>
            <div v-for="(item, index) in conceptDown" :key="`concept-down-${index}`" class="list-item">
              <div class="rank concept-rank">{{ index + 1 }}</div>
              <div class="info">
                <div class="name">{{ item.name }}</div>
                <!-- 修复：添加空值判断 -->
<div class="leader-stock">领跌股：{{ item.leaderStock }}({{ item.leaderStockCode }})<span class="fall"> {{ (Number(item.leaderStockChange) ?? 0) >= 0 ? '+' : '' }}{{ (Number(item.leaderStockChange) ?? 0).toFixed(2) }}%</span></div>
              </div>
              <div class="change-rate fall">{{ item.changeRate >= 0 ? '+' : '' }}{{ item.changeRate }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import axios from 'axios';

export default {
  name: 'MarketOverviewView',
  setup() {
    // 大盘数据
    const shIndex = ref('0.00');
    const shChange = ref(0.00);
    const shChangeRate = ref(0.00);
    const szIndex = ref('0.00');
    const szChange = ref(0.00);
    const szChangeRate = ref(0.00);
    const cyIndex = ref('0.00');
    const cyChange = ref(0.00);
    const cyChangeRate = ref(0.00);
    const upStocks = ref(0);
    const downStocks = ref(0);
    const totalAmount = ref('0.00');
    const updateTime = ref('加载中...');

    // 行业数据
    const industryUp = ref([]);
    const industryDown = ref([]);

    // 概念数据
    const conceptUp = ref([]);
    const conceptDown = ref([]);

    // 获取市场数据
    const fetchMarketData = async () => {
      try {
        const response = await axios.get('/api/market/overview');
        const data = response.data;

        // 更新大盘数据
        shIndex.value = data.shIndex;
        shChange.value = data.shChange;
        shChangeRate.value = data.shChangeRate;
        szIndex.value = data.szIndex;
        szChange.value = data.szChange;
        szChangeRate.value = data.szChangeRate;
        cyIndex.value = data.cyIndex;
        cyChange.value = data.cyChange;
        cyChangeRate.value = data.cyChangeRate;
        upStocks.value = data.upStocks;
        downStocks.value = data.downStocks;
        totalAmount.value = data.totalAmount;
        updateTime.value = data.date;

        // 分类处理行业和概念数据
        industryUp.value = data.marketHotspots.filter(item => item.type === 'industry_up');
        industryDown.value = data.marketHotspots.filter(item => item.type === 'industry_down');
        conceptUp.value = data.marketHotspots.filter(item => item.type === 'concept_up');
        conceptDown.value = data.marketHotspots.filter(item => item.type === 'concept_down');

      } catch (error) {
        console.error('市场数据获取失败:', error);
        ElMessage.error('市场数据加载失败，请刷新重试');
      }
    };

    onMounted(() => {
      fetchMarketData();
      // 每5分钟刷新一次数据
      setInterval(fetchMarketData, 5 * 60 * 1000);
    });

    return {
      shIndex, shChange, shChangeRate,
      szIndex, szChange, szChangeRate,
      cyIndex, cyChange, cyChangeRate,
      upStocks, downStocks, totalAmount, updateTime,
      industryUp, industryDown,
      conceptUp, conceptDown
    };
  }
};
</script>

<style scoped>
.market-overview-container {
  padding: 20px;
}

/* 卡片通用样式 */
.market-index-card, .industry-concept-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
  padding: 20px;
  margin-bottom: 24px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.card-title i {
  margin-right: 8px;
  font-size: 20px;
}

/* 大盘指数网格 */
.index-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.index-item {
  background: #f7f8fa;
  border-radius: 6px;
  padding: 16px;
  text-align: center;
}

.index-name {
  font-size: 14px;
  color: #86909c;
  margin-bottom: 8px;
}

.index-value {
  font-size: 24px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 4px;
}

.index-change {
  font-size: 14px;
  font-weight: 500;
}

.index-desc {
  font-size: 12px;
  color: #86909c;
  margin-top: 8px;
}

/* 涨跌颜色 */
.rise {
  color: #f53f3f;
}

.fall {
  color: #00b42a;
}

.update-time {
  font-size: 12px;
  color: #86909c;
  margin-top: 16px;
  text-align: right;
}

/* 行业/概念TOP5样式 */
.top5-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.top5-list .list-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}

.top5-list .list-title i {
  margin-right: 6px;
}

.list-container {
  background: #f7f8fa;
  border-radius: 6px;
  padding: 12px;
}

.list-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.list-item:last-child {
  border-bottom: none;
}

.rank {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  margin-right: 12px;
}

/* 行业和概念的排名颜色区分 */
.industry-rank {
  background: #e8f4f8;
  color: #36cfc9;
}

.concept-rank {
  background: #f5f0ff;
  color: #722ed1;
}

.info {
  flex: 1;
}

.name {
  font-size: 14px;
  font-weight: 500;
  color: #1d2129;
  margin-bottom: 2px;
}

.leader-stock {
  font-size: 12px;
  color: #86909c;
}

.change-rate {
  font-size: 14px;
  font-weight: 500;
  min-width: 60px;
  text-align: right;
}

.empty-tip {
  text-align: center;
  padding: 20px;
  color: #86909c;
  font-size: 14px;
}

/* 行业和概念卡片的区分 */
.industry-card .card-title i {
  color: #36cfc9;
}

.concept-card .card-title i {
  color: #722ed1;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .top5-grid {
    grid-template-columns: 1fr;
  }

  .index-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 480px) {
  .index-grid {
    grid-template-columns: 1fr;
  }
}
</style>