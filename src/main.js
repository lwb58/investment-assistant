import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import '@wangeditor/editor/dist/css/style.css'

// 导入Element Plus组件库和样式
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'





const app = createApp(App)

// 使用Element Plus并配置中文语言
app.use(ElementPlus, {
  locale: zhCn
})

app.use(router)

app.mount('#app')