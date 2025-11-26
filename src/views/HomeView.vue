<template>
  <div class="home">
    <header class="header">
      <h1>投资辅助系统</h1>
      <nav class="nav">
        <router-link to="/industry-valuation" class="nav-link">行业估值分析</router-link>
        <router-link to="/market-data" class="nav-link">市场数据中心</router-link>
        <router-link to="/financial-analysis" class="nav-link">财务分析引擎</router-link>
        <router-link to="/valuation-decision" class="nav-link">估值决策系统</router-link>
      </nav>
      <div class="user-actions">
        <router-link to="/login" class="btn">登录</router-link>
        <router-link to="/register" class="btn btn-primary">注册</router-link>
      </div>
    </header>
    
    <main class="main-content">
      <section class="hero">
        <h2>专业的投资分析与决策支持平台</h2>
        <p>基于大数据分析和智能算法，为投资者提供精准的行业估值、市场数据、财务分析和投资决策支持</p>
        <router-link to="/industry-valuation" class="btn-large btn-primary">立即体验</router-link>
      </section>
      
      <section class="features">
        <div class="feature-card">
          <h3>行业估值分析</h3>
          <p>动态估值评估、多维度对比分析、趋势预测</p>
        </div>
        <div class="feature-card">
          <h3>市场数据中心</h3>
          <p>实时行情监控、行业全景数据、自定义看板</p>
        </div>
        <div class="feature-card">
          <h3>财务分析引擎</h3>
          <p>财务指标计算、趋势可视化、风险预警</p>
        </div>
        <div class="feature-card">
          <h3>估值决策系统</h3>
          <p>个股估值分析、低估筛选、安全边际测算</p>
        </div>
      </section>
    </main>
    
    <footer class="footer">
      <p>© 2025 投资辅助系统 - 仅供参考，不构成投资建议</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
// 主页组件逻辑
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header h1 {
  margin: 0;
  color: #3059a7;
  font-size: 1.5rem;
}

.nav {
  display: flex;
  gap: 1.5rem;
}

.nav-link {
  color: #606266;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s;
}

.nav-link:hover {
  color: #3059a7;
}

.user-actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #ffffff;
  color: #606266;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s;
}

.btn:hover {
  border-color: #3059a7;
  color: #3059a7;
}

.btn-primary {
  background-color: #3059a7;
  color: #ffffff;
  border-color: #3059a7;
}

.btn-primary:hover {
  background-color: #264a8e;
  border-color: #264a8e;
  color: #ffffff;
}

.main-content {
  flex: 1;
  padding: 2rem;
}

.hero {
  text-align: center;
  padding: 3rem 0;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 8px;
  margin-bottom: 2rem;
}

.hero h2 {
  margin: 0 0 1rem 0;
  color: #3059a7;
  font-size: 2.5rem;
}

.hero p {
  margin: 0 0 2rem 0;
  color: #606266;
  font-size: 1.1rem;
  max-width: 800px;
  margin: 0 auto 2rem auto;
}

.btn-large {
  padding: 0.8rem 2rem;
  font-size: 1.1rem;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.feature-card {
  padding: 1.5rem;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.feature-card h3 {
  margin: 0 0 1rem 0;
  color: #3059a7;
  font-size: 1.2rem;
}

.feature-card p {
  margin: 0;
  color: #606266;
  font-size: 0.9rem;
}

.footer {
  padding: 1rem 2rem;
  background-color: #f5f7fa;
  text-align: center;
  color: #909399;
  font-size: 0.8rem;
}

.footer p {
  margin: 0;
}
</style>